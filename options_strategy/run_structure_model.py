"""
Walk-forward evaluation of the structure-P&L selector (phase 7).

Compares, over the same test span:
  - structure_model:   one forest per structure predicting its return on
                       capital at risk; trade the highest prediction
  - best_average:      trade whichever structure averaged best on the
                       training slice (what the forests reduce to if the
                       features carry no signal)
  - two_model:         phase 6, for reference
  - baseline:          strategy.manual_strategy (the bar to beat)
  - perfect_foresight: pick the structure with the best TRUE return each
                       day. Not a real strategy -- the ceiling on picking
  - buy_and_hold

The backtest only opens a new structure when none is open, so it trades
about one day in 20. Pick quality is also scored on every test day: the
realized return of the structure each strategy picked, ignoring overlap and
cash.

Usage:
    python3 -m options_strategy.run_structure_model --symbol SPY --start 2010-01-01 --end 2024-12-31
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from options_strategy import models
from options_strategy.backtester import FLAT
from options_strategy.structure_model import (
    CANDIDATES,
    BestAverageStrategy,
    StructurePnLStrategy,
    choose_structures,
    structure_returns,
)
from options_strategy.walk_forward import (
    add_walk_forward_args,
    baseline_signal_fn,
    buy_and_hold,
    compare,
    load_inputs,
    pricing_kwargs,
    run_walk_forward,
)


def forecast_skill(predicted: pd.DataFrame, naive: pd.DataFrame, actual: pd.DataFrame) -> pd.DataFrame:
    """Per structure: correlation of forest predictions with realized returns,
    and out-of-sample R^2 against the training-mean forecast (> 0 means the
    forest beats predicting the training average)."""
    rows = {}
    for structure in predicted.columns:
        both = pd.DataFrame(
            {"pred": predicted[structure], "naive": naive[structure], "actual": actual[structure]}
        ).dropna()
        sse_model = ((both["actual"] - both["pred"]) ** 2).sum()
        sse_naive = ((both["actual"] - both["naive"]) ** 2).sum()
        rows[structure] = {
            "days": len(both),
            "mean_actual": both["actual"].mean(),
            "mean_pred": both["pred"].mean(),
            "corr": both["pred"].corr(both["actual"]),
            "r2_vs_train_mean": 1 - sse_model / sse_naive if sse_naive > 0 else np.nan,
        }
    return pd.DataFrame(rows).T


def pick_quality(picks: pd.Series, actual: pd.DataFrame) -> dict:
    """Mean realized return of the picked structure per test day (FLAT = 0),
    over days where every structure's realized return is known."""
    known = actual.notna().all(axis=1) & picks.reindex(actual.index).notna()
    picks = picks.reindex(actual.index)[known]
    realized = [0.0 if p == FLAT else actual.at[d, p] for d, p in picks.items()]
    return {"days": len(realized), "mean_return": np.mean(realized), "flat_share": (picks == FLAT).mean()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk-forward evaluation of the structure-P&L selector.")
    add_walk_forward_args(parser)
    parser.add_argument("--min-edge", type=float, default=0.0,
                        help="Minimum predicted return on capital at risk to open a structure")
    args = parser.parse_args()

    if args.gap_days < args.holding_days:
        parser.error("--gap-days must be >= --holding-days, or forward labels leak into the test window")

    price_df, features, vol_series = load_inputs(args.symbol, args.start, args.end)
    horizon = args.holding_days
    pricing = pricing_kwargs(args)
    run_kwargs = dict(
        train_days=args.train_days,
        test_days=args.test_days,
        gap_days=args.gap_days,
        expanding=args.expanding,
        initial_capital=args.capital,
        holding_period_days=horizon,
        **pricing,
    )

    # True returns over the full history: used only for scoring and the
    # perfect-foresight ceiling, never handed to the strategies.
    actual = structure_returns(price_df, features, CANDIDATES, horizon, **pricing)

    def perfect_foresight_fn(train_features, train_prices, test_features):
        return choose_structures(actual.reindex(test_features.index), args.min_edge)

    structure_model = StructurePnLStrategy(horizon=horizon, min_edge=args.min_edge, **pricing)
    best_average = BestAverageStrategy(horizon=horizon, min_edge=args.min_edge, **pricing)
    two_model = models.TwoModelStrategy(horizon=horizon)
    print("Training and testing structure model walk-forward...")
    results = {
        "structure_model": run_walk_forward(price_df, features, vol_series, structure_model, **run_kwargs),
        "best_average": run_walk_forward(price_df, features, vol_series, best_average, **run_kwargs),
        "two_model": run_walk_forward(price_df, features, vol_series, two_model, **run_kwargs),
        "baseline": run_walk_forward(price_df, features, vol_series, baseline_signal_fn, **run_kwargs),
        "perfect_foresight": run_walk_forward(price_df, features, vol_series, perfect_foresight_fn, **run_kwargs),
    }
    splits = results["structure_model"].splits
    first, last = splits[0].test[0], splits[-1].test[-1]
    print(f"\n{len(splits)} walk-forward windows, test span {first.date()} to {last.date()}")

    table = compare(
        {name: r.backtest for name, r in results.items()}
        | {"buy_and_hold": buy_and_hold(price_df, first, last, args.capital)}
    )
    predictions = pd.concat(structure_model.predictions)
    naive = pd.concat(structure_model.training_means)
    test_actual = actual.reindex(predictions.index)

    with pd.option_context("display.width", 200, "display.max_columns", None):
        print("\nTest-span comparison:")
        print(table.drop(columns=["start_date", "end_date"]).to_string())

        print("\nForest forecast skill on test days (return on capital at risk):")
        print(forecast_skill(predictions, naive, test_actual).astype(float).round(4).to_string())

        # The baseline is left out: it also trades covered calls and
        # protective puts, which aren't candidates, so have no realized return here.
        print("\nPick quality, every test day (mean realized return of the picked structure):")
        quality = {
            name: pick_quality(results[name].signals, test_actual)
            for name in ("structure_model", "best_average", "two_model", "perfect_foresight")
        }
        print(pd.DataFrame(quality).T.astype(float).round(4).to_string())

        print("\nStructure model picks on test days:")
        print(results["structure_model"].signals.value_counts().to_string())
        print("\nBest-average pick per window:", ", ".join(best_average.picks))

        trades = pd.DataFrame([t.__dict__ for t in results["structure_model"].backtest.trades])
        if not trades.empty:
            by_structure = trades.groupby("structure_name")["pnl"].agg(
                trades="count", win_rate=lambda p: round((p > 0).mean(), 3), total_pnl="sum", worst="min"
            )
            print("\nStructure-model trades by structure:")
            print(by_structure.round(2).to_string())

        print("\nStructure model by window:")
        print(results["structure_model"].window_table().to_string(index=False))


if __name__ == "__main__":
    main()