"""
Day-by-day, mark-to-market options backtester.

Pattern follows ML4T's marketsim idea (orders/positions in, daily portfolio
value and performance stats out), but built fresh here and extended with an
options pricing layer: contract multiplier, expiry, and a bid/ask slippage
haircut, none of which plain-equity marketsim needs.

Every price in a backtest run comes from Black-Scholes off a volatility
proxy (see pricing.py / data.py), bent by a parametric skew, not a real
historical option quote. Treat
results as directional, not as a guarantee of what real fills would have
looked like. See options_strategy/PROJECT.md for the full caveat.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from options_strategy.pricing import black_scholes_price, skewed_vol, standardized_moneyness

CONTRACT_MULTIPLIER = 100
CALENDAR_DAYS_PER_YEAR = 365.0
TRADING_DAYS_PER_YEAR = 252

# Signals a strategy function can emit.
FLAT = "FLAT"
LONG_CALL = "LONG_CALL"
LONG_PUT = "LONG_PUT"
COVERED_CALL = "COVERED_CALL"
PROTECTIVE_PUT = "PROTECTIVE_PUT"
BULL_CALL_SPREAD = "BULL_CALL_SPREAD"  # call debit spread
BULL_PUT_SPREAD = "BULL_PUT_SPREAD"  # put credit spread
BEAR_CALL_SPREAD = "BEAR_CALL_SPREAD"  # call credit spread
IRON_CONDOR = "IRON_CONDOR"
CASH_SECURED_PUT = "CASH_SECURED_PUT"
SIGNALS = (
    FLAT,
    LONG_CALL,
    LONG_PUT,
    COVERED_CALL,
    PROTECTIVE_PUT,
    BULL_CALL_SPREAD,
    BULL_PUT_SPREAD,
    BEAR_CALL_SPREAD,
    IRON_CONDOR,
    CASH_SECURED_PUT,
)


@dataclass
class Leg:
    kind: str  # "stock" or "option"
    quantity: int  # +long, -short. Shares for stock; contracts for options.
    option_type: str | None = None  # "call" / "put", None for stock
    strike: float | None = None
    expiry: pd.Timestamp | None = None
    entry_price: float | None = None  # mid price at open
    entry_slippage_pct: float | None = None  # bid/ask haircut at open (options only)

    @property
    def multiplier(self) -> int:
        return CONTRACT_MULTIPLIER if self.kind == "option" else 1


@dataclass
class Structure:
    name: str
    legs: list[Leg]
    entry_date: pd.Timestamp | None = None
    exit_date: pd.Timestamp | None = None  # planned close (holding period or expiry)
    max_loss: float | None = None  # worst-case cash loss if held to expiry, set on open


@dataclass
class Trade:
    structure_name: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_cost: float  # cash spent (positive) or received (negative) to open
    exit_proceeds: float  # cash received (positive) or paid (negative) to close
    pnl: float
    max_loss: float | None = None  # capital at risk when opened (see Structure.max_loss)


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: list[Trade] = field(default_factory=list)
    skipped_for_capital: int = 0  # signals not acted on because max loss exceeded cash

    def summary(self) -> dict:
        equity = self.equity_curve.dropna()
        if len(equity) < 2:
            return {"error": "not enough data to summarize"}

        daily_returns = equity.pct_change().dropna()
        total_return = equity.iloc[-1] / equity.iloc[0] - 1
        n_days = len(equity)
        # equity.iloc[-1] can go <= 0 if a strategy loses more than the
        # starting capital (no margin/buying-power limit is enforced yet);
        # a fractional power of a non-positive base is undefined, so CAGR
        # is reported as NaN in that case instead of raising or silently
        # returning a bogus complex-derived value.
        if equity.iloc[-1] > 0:
            cagr = (equity.iloc[-1] / equity.iloc[0]) ** (TRADING_DAYS_PER_YEAR / n_days) - 1
        else:
            cagr = np.nan

        sharpe = np.nan
        if daily_returns.std() > 0:
            sharpe = (daily_returns.mean() / daily_returns.std()) * np.sqrt(TRADING_DAYS_PER_YEAR)

        running_max = equity.cummax()
        drawdown = equity / running_max - 1
        max_drawdown = drawdown.min()

        wins = [t for t in self.trades if t.pnl > 0]
        win_rate = len(wins) / len(self.trades) if self.trades else np.nan
        avg_trade_pnl = np.mean([t.pnl for t in self.trades]) if self.trades else np.nan
        worst_trade_pnl = min(t.pnl for t in self.trades) if self.trades else np.nan

        return {
            "start_date": str(equity.index[0].date()),
            "end_date": str(equity.index[-1].date()),
            "start_equity": round(equity.iloc[0], 2),
            "end_equity": round(equity.iloc[-1], 2),
            "total_return": round(total_return, 4),
            "cagr": round(cagr, 4) if not np.isnan(cagr) else None,
            "sharpe": round(sharpe, 3) if not np.isnan(sharpe) else None,
            "max_drawdown": round(max_drawdown, 4),
            "num_trades": len(self.trades),
            "win_rate": round(win_rate, 3) if not np.isnan(win_rate) else None,
            "avg_trade_pnl": round(avg_trade_pnl, 2) if not np.isnan(avg_trade_pnl) else None,
            "worst_trade_pnl": round(worst_trade_pnl, 2) if not np.isnan(worst_trade_pnl) else None,
            "skipped_for_capital": self.skipped_for_capital,
        }


def _execution_price(mid_price: float, quantity: int, opening: bool, slippage_pct: float) -> float:
    """Apply a bid/ask haircut. Buying pays the ask (above mid), selling hits
    the bid (below mid). `quantity > 0` opening = buying; closing a long
    position = selling, and vice versa for shorts.
    """
    is_buy = (quantity > 0) if opening else (quantity < 0)
    return mid_price * (1 + slippage_pct) if is_buy else mid_price * (1 - slippage_pct)


class OptionsBacktester:
    def __init__(
        self,
        price_df: pd.DataFrame,
        vol_series: pd.Series,
        initial_capital: float = 100_000.0,
        rate: float = 0.04,
        holding_period_days: int = 20,
        otm_pct: float = 0.03,
        spread_width_pct: float = 0.05,
        commission_per_contract: float = 0.65,
        option_slippage_pct: float = 0.02,
        skew_slope: float = -0.15,
        skew_curvature: float = 0.05,
        otm_slippage_mult: float = 0.5,
        atm_vol_scale: float = 1.0,
        price_col: str = "Close",
    ):
        """
        price_df: DataFrame with a DatetimeIndex and a `price_col` column.
        vol_series: annualized vol decimal (e.g. from pricing.iv_proxy_from_vix),
            aligned to price_df's index.
        holding_period_days: trading days a structure is held before being
            closed, if it doesn't reach expiry first.
        otm_pct: how far out-of-the-money to strike new options (0.03 = 3%).
        spread_width_pct: distance between the two strikes of a vertical
            spread (and of each iron condor wing), as a fraction of spot.
            Debit spreads buy at-the-money and sell this far OTM; credit
            spreads sell at otm_pct and buy the protective wing this much
            further out.
        skew_slope, skew_curvature: shape of the vol skew around the
            vol_series level, which is treated as at-the-money vol (see
            pricing.skewed_vol). Both 0 prices every strike at flat vol.
        option_slippage_pct: bid/ask haircut on an at- or in-the-money option,
            as a fraction of mid. An OTM option's haircut grows by
            otm_slippage_mult per standard deviation OTM (see _slippage_pct).
            otm_slippage_mult=0 gives the same haircut at every strike.
        atm_vol_scale: multiplies vol_series to get at-the-money vol. VIX
            runs above SPY's ATM implied vol, since it also prices the OTM
            put skew, so taking VIX as ATM vol overprices every option.
            calibrate.py measures VIX / ATM vol from chain snapshots; the
            scale is its reciprocal. 1.0 uses vol_series as-is.
        """
        self.prices = price_df[price_col]
        self.vol = vol_series.reindex(self.prices.index).ffill() * atm_vol_scale
        self.initial_capital = initial_capital
        self.rate = rate
        self.holding_period_days = holding_period_days
        self.otm_pct = otm_pct
        self.spread_width_pct = spread_width_pct
        self.commission_per_contract = commission_per_contract
        self.option_slippage_pct = option_slippage_pct
        self.skew_slope = skew_slope
        self.skew_curvature = skew_curvature
        self.otm_slippage_mult = otm_slippage_mult

    # -- structure builders -------------------------------------------------

    def _expiry_for(self, entry_idx: int) -> pd.Timestamp:
        exit_idx = min(entry_idx + self.holding_period_days, len(self.prices) - 1)
        return self.prices.index[exit_idx]

    def _time_to_expiry(self, current_date: pd.Timestamp, expiry: pd.Timestamp) -> float:
        days = max((expiry - current_date).days, 0)
        return days / CALENDAR_DAYS_PER_YEAR

    def _price_option(
        self, spot: float, strike: float, t: float, vol: float, option_type: str
    ) -> float:
        """Mid price. `vol` is at-the-money vol; the skew sets this strike's vol."""
        if t <= 0:
            return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
        strike_vol = skewed_vol(vol, spot, strike, t, slope=self.skew_slope, curvature=self.skew_curvature)
        return black_scholes_price(spot, strike, t, strike_vol, rate=self.rate, option_type=option_type)

    def _slippage_pct(
        self, spot: float, strike: float, t: float, vol: float, option_type: str
    ) -> float:
        """Bid/ask haircut as a fraction of mid: option_slippage_pct at the
        money, widened by otm_slippage_mult per standard deviation OTM. Cheap
        far-OTM options (condor and spread wings) trade at wider spreads
        relative to their price than near-the-money ones.

        At expiry (t <= 0) there's no OTM-ness to measure; an OTM option is
        worth zero there anyway, so the base haircut applies.
        """
        if t <= 0 or vol <= 0:
            return self.option_slippage_pct
        x = standardized_moneyness(vol, spot, strike, t)
        sd_otm = max(x, 0.0) if option_type == "call" else max(-x, 0.0)
        return self.option_slippage_pct * (1 + self.otm_slippage_mult * sd_otm)

    def _build_structure(self, signal: str, date: pd.Timestamp, idx: int) -> Structure | None:
        spot = self.prices.loc[date]
        vol = self.vol.loc[date]
        if pd.isna(spot) or pd.isna(vol) or vol <= 0:
            return None

        expiry = self._expiry_for(idx)
        t = self._time_to_expiry(date, expiry)
        if t <= 0:
            return None

        def _option(quantity: int, option_type: str, strike_mult: float) -> Leg:
            strike = round(spot * strike_mult, 2)
            leg = Leg("option", quantity=quantity, option_type=option_type, strike=strike, expiry=expiry)
            leg.entry_price = self._price_option(spot, strike, t, vol, option_type)
            leg.entry_slippage_pct = self._slippage_pct(spot, strike, t, vol, option_type)
            return leg

        def _stock() -> Leg:
            return Leg("stock", quantity=CONTRACT_MULTIPLIER, entry_price=spot)

        otm, width = self.otm_pct, self.spread_width_pct
        legs_by_signal = {
            LONG_CALL: lambda: [_option(1, "call", 1 + otm)],
            LONG_PUT: lambda: [_option(1, "put", 1 - otm)],
            COVERED_CALL: lambda: [_stock(), _option(-1, "call", 1 + otm)],
            PROTECTIVE_PUT: lambda: [_stock(), _option(1, "put", 1 - otm)],
            BULL_CALL_SPREAD: lambda: [_option(1, "call", 1.0), _option(-1, "call", 1 + width)],
            BULL_PUT_SPREAD: lambda: [_option(-1, "put", 1 - otm), _option(1, "put", 1 - otm - width)],
            BEAR_CALL_SPREAD: lambda: [_option(-1, "call", 1 + otm), _option(1, "call", 1 + otm + width)],
            IRON_CONDOR: lambda: [
                _option(1, "put", 1 - otm - width),
                _option(-1, "put", 1 - otm),
                _option(-1, "call", 1 + otm),
                _option(1, "call", 1 + otm + width),
            ],
            CASH_SECURED_PUT: lambda: [_option(-1, "put", 1 - otm)],
        }
        if signal not in legs_by_signal:
            return None  # FLAT or unrecognized signal

        structure = Structure(signal, legs_by_signal[signal](), entry_date=date, exit_date=expiry)
        structure.max_loss = self._max_loss(structure)
        return structure


    # -- valuation ------------------------------------------------------------

    def _leg_value(self, leg: Leg, spot: float, t: float, vol: float) -> float:
        if leg.kind == "stock":
            price = spot
        else:
            price = self._price_option(spot, leg.strike, t, vol, leg.option_type)
        return leg.quantity * price * leg.multiplier

    def _open_cost(self, structure: Structure) -> float:
        """Cash impact of opening (positive = cash spent, negative = cash received)."""
        cost = 0.0
        for leg in structure.legs:
            exec_price = (
                _execution_price(leg.entry_price, leg.quantity, opening=True, slippage_pct=leg.entry_slippage_pct)
                if leg.kind == "option"
                else leg.entry_price
            )
            cost += leg.quantity * exec_price * leg.multiplier
            if leg.kind == "option":
                cost += self.commission_per_contract * abs(leg.quantity)
        return cost

    def _close_proceeds(self, structure: Structure, spot: float, vol: float) -> float:
        """Cash impact of closing (positive = cash received, negative = cash paid)."""
        proceeds = 0.0
        for leg in structure.legs:
            if leg.kind == "stock":
                exec_price = spot
            else:
                t = self._time_to_expiry(structure.exit_date, leg.expiry)
                mid_price = self._price_option(spot, leg.strike, t, vol, leg.option_type)
                slippage_pct = self._slippage_pct(spot, leg.strike, t, vol, leg.option_type)
                exec_price = _execution_price(mid_price, leg.quantity, opening=False, slippage_pct=slippage_pct)
            # Closing settles the same side of the market the position was
            # already on: selling a long leg receives quantity*price (positive),
            # buying back a short leg pays quantity*price (quantity<0, so
            # this is negative) -- same sign convention as _open_cost, just
            # applied as `cash += proceeds` instead of `cash -= cost`.
            proceeds += leg.quantity * exec_price * leg.multiplier
            if leg.kind == "option":
                proceeds -= self.commission_per_contract * abs(leg.quantity)
        return proceeds

    def _max_loss(self, structure: Structure) -> float:
        """Worst-case cash loss if the structure is held to expiry, using the
        same open/close accounting (slippage, commissions) as the backtest.

        Every leg's payoff at expiry is piecewise linear in the underlying
        price, kinked only at strikes, so the minimum close value is at S=0,
        at a strike, or out in the upside tail. Net short calls/stock above
        the top strike (e.g. a naked short call) means unbounded loss.

        Otherwise the tail is checked at 2x the top strike rather than at
        infinity: the proportional slippage haircut makes deep-ITM short
        calls cost slightly more to buy back than their hedge returns, so
        even a covered call drifts down forever in this model. A doubling of
        the underlying within one holding period is a generous bound.
        """
        upside_slope = sum(
            leg.quantity * leg.multiplier
            for leg in structure.legs
            if leg.kind == "stock" or leg.option_type == "call"
        )
        if upside_slope < 0:
            return float("inf")
        strikes = sorted({leg.strike for leg in structure.legs if leg.kind == "option"})
        top = max(strikes, default=self.prices.loc[structure.entry_date])
        worst_close = min(self._close_proceeds(structure, s, 0.0) for s in [0.0, *strikes, top * 2])
        return self._open_cost(structure) - worst_close

    def trade_outcome(self, signal: str, idx: int) -> Trade | None:
        """Open `signal` on trading day `idx` and close it after the holding
        period, priced exactly as run() would, but ignoring cash and any
        other open position. None if the structure can't be built or the
        holding period runs past the end of the price history.
        """
        if idx + self.holding_period_days >= len(self.prices):
            return None
        date = self.prices.index[idx]
        structure = self._build_structure(signal, date, idx)
        if structure is None:
            return None
        exit_date = structure.exit_date
        proceeds = self._close_proceeds(structure, self.prices.loc[exit_date], self.vol.loc[exit_date])
        entry_cost = self._open_cost(structure)
        return Trade(
            structure_name=signal,
            entry_date=date,
            exit_date=exit_date,
            entry_cost=entry_cost,
            exit_proceeds=proceeds,
            pnl=proceeds - entry_cost,
            max_loss=structure.max_loss,
        )

    # -- main loop --------------------------------------------------------

    def run(self, signals: pd.Series) -> BacktestResult:
        """`signals` is a Series aligned to price_df's index with values from
        the signal constants at the top of this module (FLAT, LONG_CALL, ...).

        A new structure is only opened when no structure is currently open.
        Once open, it's held until its planned exit_date regardless of later
        signal changes (avoids unrealistic same-day flip-flopping).

        A structure is only opened if current cash covers both its opening
        cost and its max loss at expiry -- a simple stand-in for broker
        buying-power rules, so short-vol structures can't lose money the
        account never had. Signals skipped for this are counted in
        `BacktestResult.skipped_for_capital`.
        """
        dates = self.prices.index
        cash = self.initial_capital
        open_structure: Structure | None = None
        equity_curve = pd.Series(index=dates, dtype=float)
        trades: list[Trade] = []
        skipped_for_capital = 0

        for idx, date in enumerate(dates):
            spot = self.prices.loc[date]
            vol = self.vol.loc[date]

            if open_structure is not None and date >= open_structure.exit_date:
                proceeds = self._close_proceeds(open_structure, spot, vol)
                cash += proceeds
                entry_cost = self._open_cost(open_structure)
                trades.append(
                    Trade(
                        structure_name=open_structure.name,
                        entry_date=open_structure.entry_date,
                        exit_date=date,
                        entry_cost=entry_cost,
                        exit_proceeds=proceeds,
                        pnl=proceeds - entry_cost,
                        max_loss=open_structure.max_loss,
                    )
                )
                open_structure = None

            if open_structure is None:
                signal = signals.get(date, FLAT)
                if signal != FLAT:
                    candidate = self._build_structure(signal, date, idx)
                    if candidate is not None:
                        open_cost = self._open_cost(candidate)
                        if max(open_cost, candidate.max_loss) > cash:
                            skipped_for_capital += 1
                        else:
                            cash -= open_cost
                            open_structure = candidate

            # Mark to market.
            mtm = 0.0
            if open_structure is not None:
                t_now_by_leg = {}
                for leg in open_structure.legs:
                    t = (
                        self._time_to_expiry(date, leg.expiry)
                        if leg.kind == "option"
                        else 0.0
                    )
                    mtm += self._leg_value(leg, spot, t, vol)
            equity_curve.loc[date] = cash + mtm

        # Force-close anything still open at the end of the backtest so the
        # final equity value reflects a realized position, not a paper one.
        if open_structure is not None:
            last_date = dates[-1]
            spot = self.prices.loc[last_date]
            vol = self.vol.loc[last_date]
            proceeds = self._close_proceeds(open_structure, spot, vol)
            cash += proceeds
            entry_cost = self._open_cost(open_structure)
            trades.append(
                Trade(
                    structure_name=open_structure.name,
                    entry_date=open_structure.entry_date,
                    exit_date=last_date,
                    entry_cost=entry_cost,
                    exit_proceeds=proceeds,
                    pnl=proceeds - entry_cost,
                    max_loss=open_structure.max_loss,
                )
            )
            equity_curve.loc[last_date] = cash

        return BacktestResult(
            equity_curve=equity_curve, trades=trades, skipped_for_capital=skipped_for_capital
        )
