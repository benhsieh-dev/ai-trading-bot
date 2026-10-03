"""
Walk-forward evaluation harness: the only way any strategy in this module
(rule-based or ML) should be scored.

History is cut into consecutive windows of [train | gap | test]. For each
window, a signal function sees only that window's training slice and returns
signals for the test dates; the test signals are stitched together and run
through one OptionsBacktester over the full test span. No random splits.

The gap is what keeps labels honest: a label like "forward 20-day return"
on the last training day is built from prices 20 days later. As long as the
gap is at least the label horizon, those prices fall before the test window
starts. Signal functions receive only the training slice of prices, so the
last `horizon` rows of a forward label come out NaN rather than peeking.

Features are computed once over the full history before slicing. That's
safe because every indicator in indicators.py is trailing-only (rolling /
ewm / shift(+n)). A future indicator that looks forward would break this.

Usage:
    python3 -m options_strategy.walk_forward --symbol SPY --start 2010-01-01 --end 2024-12-31
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Callable, Iterator

import pandas as pd

from options_strategy import data, indicators, strategy
from options_strategy.backtester import FLAT, SIGNALS, BacktestResult, OptionsBacktester
from options_strategy.run_backtest import BROAD_MARKET_PROXIES, build_vol_series

# (train_features, train_prices, test_features) -> signals indexed by test_features.index.
# train_prices is the price_df slice (Close, VIX, ...) for the training dates only.
SignalFn = Callable[[pd.DataFrame, pd.DataFrame, pd.DataFrame], pd.Series]


@dataclass
class Split:
    train: pd.DatetimeIndex
    test: pd.DatetimeIndex


def walk_forward_splits(
    index: pd.DatetimeIndex,
    train_days: int = 756,
    test_days: int = 126,
    gap_days: int = 20,
    expanding: bool = False,
) -> Iterator[Split]:
    """Yield train/test date splits over `index` (trading days).

    Test windows are consecutive and non-overlapping. With `expanding`, every
    training window starts at the beginning of history; otherwise it's a
    rolling `train_days` window. A final test window shorter than
    `test_days` is kept, as long as it's non-empty.
    """
    n = len(index)
    test_start = train_days + gap_days
    while test_start < n:
        test_end = min(test_start + test_days, n)
        train_end = test_start - gap_days
        train_start = 0 if expanding else train_end - train_days
        yield Split(train=index[train_start:train_end], test=index[test_start:test_end])
        test_start = test_end


@dataclass
class WalkForwardResult:
    backtest: BacktestResult
    signals: pd.Series  # stitched test-window signals over the test span
    splits: list[Split]

    def window_table(self) -> pd.DataFrame:
        """Per-test-window return, max drawdown and trades opened."""
        equity = self.backtest.equity_curve
        rows = []
        prev_equity = equity.iloc[0]
        for split in self.splits:
            window_eq = equity.loc[split.test[0] : split.test[-1]]
            path = pd.concat([pd.Series([prev_equity]), window_eq.reset_index(drop=True)])
            opened = [t for t in self.backtest.trades if split.test[0] <= t.entry_date <= split.test[-1]]
            rows.append(
                {
                    "train": f"{split.train[0].date()} to {split.train[-1].date()}",
                    "test": f"{split.test[0].date()} to {split.test[-1].date()}",
                    "return": round(window_eq.iloc[-1] / prev_equity - 1, 4),
                    "max_drawdown": round((path / path.cummax() - 1).min(), 4),
                    "trades_opened": len(opened),
                    "trade_pnl": round(sum(t.pnl for t in opened), 2),
                }
            )
            prev_equity = window_eq.iloc[-1]
        return pd.DataFrame(rows)


def run_walk_forward(
    price_df: pd.DataFrame,
    features: pd.DataFrame,
    vol_series: pd.Series,
    signal_fn: SignalFn,
    train_days: int = 756,
    test_days: int = 126,
    gap_days: int = 20,
    expanding: bool = False,
    **backtester_kwargs,
) -> WalkForwardResult:
    """Run `signal_fn` walk-forward and backtest the stitched test signals.

    The backtest covers only the span from the first test date to the last,
    so stats aren't diluted by the untraded initial training period.
    `backtester_kwargs` pass through to OptionsBacktester (holding period,
    otm_pct, capital, ...). Keep gap_days >= the holding period / label horizon.
    """
    splits = list(walk_forward_splits(features.index, train_days, test_days, gap_days, expanding))
    if not splits:
        raise ValueError(
            f"Not enough history for one split: {len(features)} days < train {train_days} + gap {gap_days} + 1"
        )

    pieces = []
    for split in splits:
        # Positional guard: the training slice must end gap_days before the test window.
        assert features.index.get_loc(split.test[0]) - features.index.get_loc(split.train[-1]) > gap_days
        window_signals = signal_fn(
            features.loc[split.train], price_df.loc[split.train], features.loc[split.test]
        )
        window_signals = window_signals.reindex(split.test).fillna(FLAT)
        unknown = set(window_signals.unique()) - set(SIGNALS)
        if unknown:
            raise ValueError(f"signal_fn returned unknown signals: {sorted(unknown)}")
        pieces.append(window_signals)
    signals = pd.concat(pieces)

    span = slice(splits[0].test[0], splits[-1].test[-1])
    backtester = OptionsBacktester(
        price_df=price_df.loc[span], vol_series=vol_series.loc[span], **backtester_kwargs
    )
    return WalkForwardResult(backtest=backtester.run(signals), signals=signals, splits=splits)


def buy_and_hold(
    price_df: pd.DataFrame, start, end, initial_capital: float = 100_000.0, price_col: str = "Close"
) -> BacktestResult:
    """Benchmark: put all capital into the underlying on `start`, hold to `end`."""
    prices = price_df[price_col].loc[start:end]
    shares = initial_capital / prices.iloc[0]
    return BacktestResult(equity_curve=shares * prices)


def baseline_signal_fn(
    train_features: pd.DataFrame, train_prices: pd.DataFrame, test_features: pd.DataFrame
) -> pd.Series:
    """The rule-based baseline needs no training; it just ignores the train slice."""
    return strategy.manual_strategy(test_features)


def compare(results: dict[str, BacktestResult]) -> pd.DataFrame:
    """Side-by-side summary table, one row per strategy."""
    return pd.DataFrame({name: r.summary() for name, r in results.items()}).T


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk-forward evaluation of the rule-based baseline.")
    parser.add_argument("--symbol", default="SPY")
    parser.add_argument("--start", default="2010-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--capital", type=float, default=100_000.0)
    parser.add_argument("--train-days", type=int, default=756, help="Trading days per training window (~3 years)")
    parser.add_argument("--test-days", type=int, default=126, help="Trading days per test window (~6 months)")
    parser.add_argument("--gap-days", type=int, default=20, help="Trading days between train and test (>= holding period)")
    parser.add_argument("--expanding", action="store_true", help="Expanding instead of rolling training window")
    parser.add_argument("--holding-days", type=int, default=20)
    args = parser.parse_args()

    if args.gap_days < args.holding_days:
        parser.error("--gap-days must be >= --holding-days, or forward labels leak into the test window")

    print(f"Fetching {args.symbol} history from {args.start} to {args.end or 'today'}...")
    price_df = data.get_price_history(args.symbol, args.start, args.end)
    vix = None
    if args.symbol.upper() in BROAD_MARKET_PROXIES:
        vix = data.get_vix_history(args.start, args.end)
        price_df = data.align_to_trading_days(price_df, vix)
    features = indicators.build_feature_frame(price_df, vix=vix)
    vol_series = build_vol_series(features)

    result = run_walk_forward(
        price_df,
        features,
        vol_series,
        baseline_signal_fn,
        train_days=args.train_days,
        test_days=args.test_days,
        gap_days=args.gap_days,
        expanding=args.expanding,
        initial_capital=args.capital,
        holding_period_days=args.holding_days,
    )
    first, last = result.splits[0].test[0], result.splits[-1].test[-1]
    print(f"\n{len(result.splits)} walk-forward windows, test span {first.date()} to {last.date()}")

    table = compare(
        {
            "baseline": result.backtest,
            "buy_and_hold": buy_and_hold(price_df, first, last, args.capital),
        }
    )
    with pd.option_context("display.width", 200, "display.max_columns", None):
        print("\nTest-span comparison:")
        print(table.drop(columns=["start_date", "end_date"]).to_string())
        print("\nBaseline by window:")
        print(result.window_table().to_string(index=False))


if __name__ == "__main__":
    main()