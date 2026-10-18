"""
Walk-forward evaluation of the two-model structure selector (phase 6).

Compares, over the same test span:
  - two_model:        direction + vol forests, mapped through models.RULE_TABLE
  - baseline:         strategy.manual_strategy (the bar to beat)
  - perfect_foresight: the rule table fed the TRUE future labels. Not a real
                      strategy -- it's the ceiling on what the rule table can
                      earn if both models were always right (the options
                      version of ML4T's theoretically optimal strategy)
  - buy_and_hold

Then scores each model on its own against "always predict the most common
class", which is what a forest learns when the features carry no signal.

Usage:
    python3 -m options_strategy.run_two_model --symbol SPY --start 2010-01-01 --end 2024-12-31
"""

from __future__ import annotations

import argparse

import pandas as pd
from sklearn.metrics import balanced_accuracy_score

from options_strategy import models
from options_strategy.walk_forward import (
    add_walk_forward_args,
    baseline_signal_fn,
    buy_and_hold,
    compare,
    load_inputs,
    pricing_kwargs,
    run_walk_forward,
)


def score_model(name: str, predicted: pd.Series, actual: pd.Series) -> None:
    both = pd.DataFrame({"predicted": predicted, "actual": actual}).dropna()
    accuracy = (both["predicted"] == both["actual"]).mean()
    majority_class = both["actual"].value_counts().idxmax()
    majority_accuracy = (both["actual"] == majority_class).mean()
    print(f"\n{name} model ({len(both)} test days):")
    print(
        f"  accuracy {accuracy:.3f} vs always-'{majority_class}' {majority_accuracy:.3f}; "
        f"balanced accuracy {balanced_accuracy_score(both['actual'], both['predicted']):.3f} "
        f"(chance = {1 / both['actual'].nunique():.3f})"
    )
    print("  rows = actual, columns = predicted:")
    table = pd.crosstab(both["actual"], both["predicted"])
    print("    " + table.to_string().replace("\n", "\n    "))


def main() -> None:
    parser = argparse.ArgumentParser(description="Walk-forward evaluation of the two-model structure selector.")
    add_walk_forward_args(parser)
    parser.add_argument("--direction-threshold", type=float, default=0.5,
                        help="Forward move, in implied-move units, that counts as bullish/bearish")
    args = parser.parse_args()

    if args.gap_days < args.holding_days:
        parser.error("--gap-days must be >= --holding-days, or forward labels leak into the test window")

    price_df, features, vol_series = load_inputs(args.symbol, args.start, args.end)
    horizon = args.holding_days
    run_kwargs = dict(
        train_days=args.train_days,
        test_days=args.test_days,
        gap_days=args.gap_days,
        expanding=args.expanding,
        initial_capital=args.capital,
        holding_period_days=args.holding_days,
        **pricing_kwargs(args),
    )

    # True labels over the full history: used only for scoring and the
    # perfect-foresight ceiling, never handed to the two-model strategy.
    true_direction = models.direction_labels(price_df, features, horizon, args.direction_threshold)
    true_vol = models.vol_labels(price_df, features, horizon)

    def perfect_foresight_fn(train_features, train_prices, test_features):
        idx = test_features.index
        return models.map_to_signals(true_direction.reindex(idx), true_vol.reindex(idx))

    two_model = models.TwoModelStrategy(horizon=horizon, direction_threshold=args.direction_threshold)
    print("Training and testing two-model strategy walk-forward...")
    results = {
        "two_model": run_walk_forward(price_df, features, vol_series, two_model, **run_kwargs),
        "baseline": run_walk_forward(price_df, features, vol_series, baseline_signal_fn, **run_kwargs),
        "perfect_foresight": run_walk_forward(price_df, features, vol_series, perfect_foresight_fn, **run_kwargs),
    }
    splits = results["two_model"].splits
    first, last = splits[0].test[0], splits[-1].test[-1]
    print(f"\n{len(splits)} walk-forward windows, test span {first.date()} to {last.date()}")

    table = compare(
        {name: r.backtest for name, r in results.items()}
        | {"buy_and_hold": buy_and_hold(price_df, first, last, args.capital)}
    )
    predictions = pd.concat(two_model.predictions)

    with pd.option_context("display.width", 200, "display.max_columns", None):
        print("\nTest-span comparison:")
        print(table.drop(columns=["start_date", "end_date"]).to_string())

        score_model("Direction", predictions["direction"], true_direction.reindex(predictions.index))
        score_model("Vol (cheap/rich)", predictions["vol"], true_vol.reindex(predictions.index))

        trades = pd.DataFrame([t.__dict__ for t in results["two_model"].backtest.trades])
        if not trades.empty:
            by_structure = trades.groupby("structure_name")["pnl"].agg(
                trades="count", win_rate=lambda p: round((p > 0).mean(), 3), total_pnl="sum", worst="min"
            )
            print("\nTwo-model trades by structure:")
            print(by_structure.round(2).to_string())

        print("\nTwo-model by window:")
        print(results["two_model"].window_table().to_string(index=False))


if __name__ == "__main__":
    main()