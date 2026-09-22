"""
CLI entry point: fetch data, compute features, run the rule-based baseline
strategy through the options backtester, and print a performance summary.

This is phase 5 of options_strategy/PROJECT.md (the rule-based baseline).
Later phases plug ML-generated signals into the same OptionsBacktester in
place of `strategy.manual_strategy`.

Usage:
    python3 -m options_strategy.run_backtest --symbol SPY --start 2018-01-01
"""

from __future__ import annotations

import argparse

import numpy as np
import pandas as pd

from options_strategy import data, indicators, pricing, strategy
from options_strategy.backtester import OptionsBacktester

# Symbols where VIX is a reasonable market-implied-vol proxy. Anything else
# falls back to a realized-vol-based proxy (see pricing.iv_proxy_fallback).
BROAD_MARKET_PROXIES = {"SPY", "QQQ", "IWM", "DIA"}


def build_vol_series(features: pd.DataFrame) -> pd.Series:
    if "vix" in features.columns:
        return pricing.iv_proxy_from_vix(features["vix"])
    return features["realized_vol_20"].apply(
        lambda rv: pricing.iv_proxy_fallback(rv) if pd.notna(rv) else np.nan
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest the rule-based options strategy.")
    parser.add_argument("--symbol", default="SPY")
    parser.add_argument("--start", default="2018-01-01")
    parser.add_argument("--end", default=None)
    parser.add_argument("--capital", type=float, default=100_000.0)
    parser.add_argument("--holding-days", type=int, default=20, help="Trading days per structure")
    parser.add_argument("--otm-pct", type=float, default=0.03)
    parser.add_argument("--out", default=None, help="CSV path to save the equity curve")
    args = parser.parse_args()

    print(f"Fetching {args.symbol} history from {args.start} to {args.end or 'today'}...")
    price_df = data.get_price_history(args.symbol, args.start, args.end)

    vix = None
    if args.symbol.upper() in BROAD_MARKET_PROXIES:
        vix = data.get_vix_history(args.start, args.end)
        price_df = data.align_to_trading_days(price_df, vix)
    else:
        print(f"Note: no VIX-based IV proxy for {args.symbol}; falling back to realized-vol proxy.")

    features = indicators.build_feature_frame(price_df, vix=vix)
    vol_series = build_vol_series(features)

    signals = strategy.manual_strategy(features)
    print("\nSignal counts:")
    print(signals.value_counts().to_string())

    backtester = OptionsBacktester(
        price_df=price_df,
        vol_series=vol_series,
        initial_capital=args.capital,
        holding_period_days=args.holding_days,
        otm_pct=args.otm_pct,
    )
    result = backtester.run(signals)

    print("\nPerformance summary:")
    for key, value in result.summary().items():
        print(f"  {key}: {value}")

    if args.out:
        result.equity_curve.to_csv(args.out)
        print(f"\nEquity curve saved to {args.out}")


if __name__ == "__main__":
    main()
