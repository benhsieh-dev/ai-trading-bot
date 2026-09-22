"""
Rule-based baseline strategy (the "ManualStrategy" pattern from ML4T,
reimplemented fresh here): turns the indicator feature frame into a daily
options signal. Every ML model built later has to beat this before it's
worth using.

Signal mapping (deliberately simple and explainable, not tuned):

              IV cheap (options underpriced)   IV rich (options overpriced)
Bullish       LONG_CALL                        COVERED_CALL
Bearish       LONG_PUT                         PROTECTIVE_PUT

COVERED_CALL and PROTECTIVE_PUT both include a stock leg (see backtester.py) --
they're not pure hedges on an existing position, they open the stock leg too.
When there's no IV-vs-realized-vol proxy available (only broad-market
symbols get a VIX-based one), the strategy falls back to the simpler
LONG_CALL / LONG_PUT / FLAT split.
"""

from __future__ import annotations

import pandas as pd

from options_strategy.backtester import COVERED_CALL, FLAT, LONG_CALL, LONG_PUT, PROTECTIVE_PUT


def manual_strategy(
    features: pd.DataFrame,
    momentum_threshold: float = 0.01,
    rsi_overbought: float = 70.0,
    rsi_oversold: float = 30.0,
    iv_rich_threshold: float = 0.02,
) -> pd.Series:
    """Rule-based signal generator. Returns a Series of signal strings
    aligned to `features.index`.
    """
    signals = pd.Series(FLAT, index=features.index)

    bullish = (
        (features["momentum_20"] > momentum_threshold)
        & (features["sma_ratio_20"] > 1.0)
        & (features["rsi_14"] < rsi_overbought)
    )
    bearish = (
        (features["momentum_20"] < -momentum_threshold)
        & (features["sma_ratio_20"] < 1.0)
        & (features["rsi_14"] > rsi_oversold)
    )

    if "iv_rv_gap_20" in features.columns:
        iv_rich = features["iv_rv_gap_20"] > iv_rich_threshold
        signals[bullish & ~iv_rich] = LONG_CALL
        signals[bullish & iv_rich] = COVERED_CALL
        signals[bearish & ~iv_rich] = LONG_PUT
        signals[bearish & iv_rich] = PROTECTIVE_PUT
    else:
        signals[bullish] = LONG_CALL
        signals[bearish] = LONG_PUT

    # Don't trade on rows where the underlying indicators are still warming
    # up (rolling-window NaNs at the start of the series).
    required_cols = ["momentum_20", "sma_ratio_20", "rsi_14"]
    missing = features[required_cols].isna().any(axis=1)
    signals[missing] = FLAT

    return signals
