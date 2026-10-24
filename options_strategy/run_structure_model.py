"""
Walk-forward evaluation of the structure-P&L selector (phase 7).

Compares it against the phase 6 two-model selector, the rule-based baseline,
a naive "trade the structure with the best training-average return" pick, a
perfect-foresight ceiling (trade the structure that actually paid best) and
buy-and-hold. Then scores each structure's forest on its own: correlation of
predicted with realized return, and out-of-sample R^2 against forecasting
the training-window mean, which is what a forest learns when the features
carry no signal.

Usage:
    python3 -m options_strategy.run_structure_model --symbol SPY --start 2010-01-01 --end 2024-12-31
"""

from __future__ import annotations

import argparse

import pandas as pd

from options_strategy import models, structure_model
from options_strategy.walk_forward import (
    add_walk_forward_args,
    baseline_signal_fn,
    buy_and_hold,
    compare,
    load_inputs,
    pricing_kwargs,
    run_walk_forward,
)


def score_forests(predicted: pd.DataFrame, naive: pd.DataFrame, actual: pd.DataFrame) -> pd.DataFrame:
    """Per structure: correlation of predicted with realized return, and R^2
    of the forest relative to forecasting the training-window mean (above 0
    means the forest beats the naive forecast)."""
    rows = {}
    for structure in predicted.columns:
        both = pd.DataFrame(
            {"pred": predicted[structure], "naive": naive[structure], "actual": actual[structure]}
        ).dropna()
        forest_sse = ((both["actual"] - both["pred"]) ** 2).sum()
        naive_sse = ((both["actual"] - both["naive"]) ** 2).sum()
        rows[structure] = {
            "days": len(both),
            "mean_realized": both["actual"].mean(),
            "corr": both["pred"].corr(both["actual"]),
            "rank_corr": both["pred"].corr(both["actual"], method="spearman"),
            "r2_vs_naive": 1 - forest_sse / naive_sse,
        }
    return pd.DataFrame(rows).T


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

    # Realized returns over the full history: used only for scoring and the
    # perfect-foresight ceiling, never handed to a strategy.
    actual = structure_model.structure_returns(price_df, features, horizon=horizon, **pricing)

    def perfect_foresight_fn(train_features, train_prices, test_features):
        return structure_model.choose_structures(actual.reindex(test_features.index), args.min_edge)

    structure_pnl = structure_model.StructurePnLStrategy(horizon=horizon, min_edge=args.min_edge, **pricing)
    best_average = structure_model.BestAverageStrategy(horizon=horizon, min_edge=args.min_edge, **pricing)
    print("Training and testing structure-P&L strategy walk-forward...")
    results = {
        "structure_pnl": run_walk_forward(price_df, features, vol_series, structure_pnl, **run_kwargs),
        "best_average": run_walk_forward(price_df, features, vol_series, best_average, **run_kwargs),
        "two_model": run_walk_forward(
            price_df, features, vol_series, models.TwoModelStrategy(horizon=horizon), **run_kwargs
        ),
        "baseline": run_walk_forward(price_df, features, vol_series, baseline_signal_fn, **run_kwargs),
        "perfect_foresight": run_walk_forward(price_df, features, vol_series, perfect_foresight_fn, **run_kwargs),
    }
    splits = results["structure_pnl"].splits
    first, last = splits[0].test[0], splits[-1].test[-1]
    print(f"\n{len(splits)} walk-forward windows, test span {first.date()} to {last.date()}")

    table = compare(
        {name: r.backtest for name, r in results.items()}
        | {"buy_and_hold": buy_and_hold(price_df, first, last, args.capital)}
    )
    predictions = pd.concat(structure_pnl.predictions)
    training_means = pd.concat(structure_pnl.training_means)

    with pd.option_context("display.width", 200, "display.max_columns", None):
        print("\nTest-span comparison:")
        print(table.drop(columns=["start_date", "end_date"]).to_string())

        print("\nPer-structure forests, out of sample (returns on capital at risk):")
        print(score_forests(predictions, training_means, actual.reindex(predictions.index)).round(3).to_string())

        chosen = results["structure_pnl"].signals
        print("\nStructure-P&L daily picks (before the one-open-position rule):")
        print(chosen.value_counts().to_string())
        print(f"\nBest-average picks by window: {pd.Series(best_average.picks).value_counts().to_dict()}")

        trades = pd.DataFrame([t.__dict__ for t in results["structure_pnl"].backtest.trades])
        if not trades.empty:
            by_structure = trades.groupby("structure_name")["pnl"].agg(
                trades="count", win_rate=lambda p: round((p > 0).mean(), 3), total_pnl="sum", worst="min"
            )
            print("\nStructure-P&L trades by structure:")
            print(by_structure.round(2).to_string())

        print("\nStructure-P&L by window:")
        print(results["structure_pnl"].window_table().to_string(index=False))


if __name__ == "__main__":
    main()
