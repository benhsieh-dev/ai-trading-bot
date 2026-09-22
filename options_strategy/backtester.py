"""
Day-by-day, mark-to-market options backtester.

Pattern follows ML4T's marketsim idea (orders/positions in, daily portfolio
value and performance stats out), but built fresh here and extended with an
options pricing layer: contract multiplier, expiry, and a bid/ask slippage
haircut, none of which plain-equity marketsim needs.

Every price in a backtest run comes from Black-Scholes off a volatility
proxy (see pricing.py / data.py), not a real historical option quote. Treat
results as directional, not as a guarantee of what real fills would have
looked like. See options_strategy/PROJECT.md for the full caveat.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from options_strategy.pricing import black_scholes_price

CONTRACT_MULTIPLIER = 100
CALENDAR_DAYS_PER_YEAR = 365.0
TRADING_DAYS_PER_YEAR = 252

# Signals a strategy function can emit.
FLAT = "FLAT"
LONG_CALL = "LONG_CALL"
LONG_PUT = "LONG_PUT"
COVERED_CALL = "COVERED_CALL"
PROTECTIVE_PUT = "PROTECTIVE_PUT"


@dataclass
class Leg:
    kind: str  # "stock" or "option"
    quantity: int  # +long, -short. Shares for stock; contracts for options.
    option_type: str | None = None  # "call" / "put", None for stock
    strike: float | None = None
    expiry: pd.Timestamp | None = None
    entry_price: float | None = None  # execution price, set once opened

    @property
    def multiplier(self) -> int:
        return CONTRACT_MULTIPLIER if self.kind == "option" else 1


@dataclass
class Structure:
    name: str
    legs: list[Leg]
    entry_date: pd.Timestamp | None = None
    exit_date: pd.Timestamp | None = None  # planned close (holding period or expiry)


@dataclass
class Trade:
    structure_name: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_cost: float  # cash spent (positive) or received (negative) to open
    exit_proceeds: float  # cash received (positive) or paid (negative) to close
    pnl: float


@dataclass
class BacktestResult:
    equity_curve: pd.Series
    trades: list[Trade] = field(default_factory=list)

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
        commission_per_contract: float = 0.65,
        option_slippage_pct: float = 0.02,
        price_col: str = "Close",
    ):
        """
        price_df: DataFrame with a DatetimeIndex and a `price_col` column.
        vol_series: annualized vol decimal (e.g. from pricing.iv_proxy_from_vix),
            aligned to price_df's index.
        holding_period_days: trading days a structure is held before being
            closed, if it doesn't reach expiry first.
        otm_pct: how far out-of-the-money to strike new options (0.03 = 3%).
        """
        self.prices = price_df[price_col]
        self.vol = vol_series.reindex(self.prices.index).ffill()
        self.initial_capital = initial_capital
        self.rate = rate
        self.holding_period_days = holding_period_days
        self.otm_pct = otm_pct
        self.commission_per_contract = commission_per_contract
        self.option_slippage_pct = option_slippage_pct

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
        if t <= 0:
            return max(spot - strike, 0.0) if option_type == "call" else max(strike - spot, 0.0)
        return black_scholes_price(spot, strike, t, vol, rate=self.rate, option_type=option_type)

    def _build_structure(self, signal: str, date: pd.Timestamp, idx: int) -> Structure | None:
        spot = self.prices.loc[date]
        vol = self.vol.loc[date]
        if pd.isna(spot) or pd.isna(vol) or vol <= 0:
            return None

        expiry = self._expiry_for(idx)
        t = self._time_to_expiry(date, expiry)
        if t <= 0:
            return None

        def _price(strike: float, option_type: str) -> float:
            return self._price_option(spot, strike, t, vol, option_type)

        if signal == LONG_CALL:
            strike = round(spot * (1 + self.otm_pct), 2)
            leg = Leg("option", quantity=1, option_type="call", strike=strike, expiry=expiry)
            leg.entry_price = _price(strike, "call")
            return Structure("LONG_CALL", [leg], entry_date=date, exit_date=expiry)

        if signal == LONG_PUT:
            strike = round(spot * (1 - self.otm_pct), 2)
            leg = Leg("option", quantity=1, option_type="put", strike=strike, expiry=expiry)
            leg.entry_price = _price(strike, "put")
            return Structure("LONG_PUT", [leg], entry_date=date, exit_date=expiry)

        if signal == COVERED_CALL:
            stock_leg = Leg("stock", quantity=CONTRACT_MULTIPLIER, entry_price=spot)
            strike = round(spot * (1 + self.otm_pct), 2)
            call_leg = Leg("option", quantity=-1, option_type="call", strike=strike, expiry=expiry)
            call_leg.entry_price = _price(strike, "call")
            return Structure("COVERED_CALL", [stock_leg, call_leg], entry_date=date, exit_date=expiry)

        if signal == PROTECTIVE_PUT:
            stock_leg = Leg("stock", quantity=CONTRACT_MULTIPLIER, entry_price=spot)
            strike = round(spot * (1 - self.otm_pct), 2)
            put_leg = Leg("option", quantity=1, option_type="put", strike=strike, expiry=expiry)
            put_leg.entry_price = _price(strike, "put")
            return Structure("PROTECTIVE_PUT", [stock_leg, put_leg], entry_date=date, exit_date=expiry)

        return None  # FLAT or unrecognized signal

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
                _execution_price(leg.entry_price, leg.quantity, opening=True, slippage_pct=self.option_slippage_pct)
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
                mid_price = spot
            else:
                t = self._time_to_expiry(structure.exit_date, leg.expiry)
                mid_price = self._price_option(spot, leg.strike, t, vol, leg.option_type)
            exec_price = (
                _execution_price(mid_price, leg.quantity, opening=False, slippage_pct=self.option_slippage_pct)
                if leg.kind == "option"
                else mid_price
            )
            # Closing settles the same side of the market the position was
            # already on: selling a long leg receives quantity*price (positive),
            # buying back a short leg pays quantity*price (quantity<0, so
            # this is negative) -- same sign convention as _open_cost, just
            # applied as `cash += proceeds` instead of `cash -= cost`.
            proceeds += leg.quantity * exec_price * leg.multiplier
            if leg.kind == "option":
                proceeds -= self.commission_per_contract * abs(leg.quantity)
        return proceeds

    # -- main loop --------------------------------------------------------

    def run(self, signals: pd.Series) -> BacktestResult:
        """`signals` is a Series aligned to price_df's index with values from
        {FLAT, LONG_CALL, LONG_PUT, COVERED_CALL, PROTECTIVE_PUT}.

        A new structure is only opened when no structure is currently open.
        Once open, it's held until its planned exit_date regardless of later
        signal changes (avoids unrealistic same-day flip-flopping).
        """
        dates = self.prices.index
        cash = self.initial_capital
        open_structure: Structure | None = None
        equity_curve = pd.Series(index=dates, dtype=float)
        trades: list[Trade] = []

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
                    )
                )
                open_structure = None

            if open_structure is None:
                signal = signals.get(date, FLAT)
                if signal != FLAT:
                    candidate = self._build_structure(signal, date, idx)
                    if candidate is not None:
                        cash -= self._open_cost(candidate)
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
                )
            )
            equity_curve.loc[last_date] = cash

        return BacktestResult(equity_curve=equity_curve, trades=trades)
