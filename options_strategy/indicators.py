"""
Technical and volatility indicators used as ML features for the options
strategy signal engine.

These are fresh, independent implementations of standard indicators (the
same ones covered conceptually in ML4T's indicator_evaluation project), not
copies of any ML4T source file.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sma(prices: pd.Series, window: int = 20) -> pd.Series:
    """Simple moving average."""
    return prices.rolling(window=window, min_periods=window).mean()


def sma_ratio(prices: pd.Series, window: int = 20) -> pd.Series:
    """Price divided by its SMA. >1 means price is above its moving average."""
    return prices / sma(prices, window)


def bollinger_percent_b(prices: pd.Series, window: int = 20, num_std: float = 2.0) -> pd.Series:
    """%B: where price sits within its Bollinger Bands.
    0 = at the lower band, 1 = at the upper band, can exceed [0, 1].
    """
    mid = sma(prices, window)
    std = prices.rolling(window=window, min_periods=window).std()
    upper = mid + num_std * std
    lower = mid - num_std * std
    band_width = upper - lower
    return (prices - lower) / band_width.replace(0, np.nan)


def momentum(prices: pd.Series, window: int = 10) -> pd.Series:
    """N-day price momentum: (price / price N days ago) - 1."""
    return prices / prices.shift(window) - 1


def rsi(prices: pd.Series, window: int = 14) -> pd.Series:
    """Relative Strength Index using Wilder's smoothing."""
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    result = 100 - (100 / (1 + rs))
    # Where avg_loss is 0 (no down days), RSI is 100.
    result = result.where(avg_loss != 0, 100.0)
    return result


def macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """MACD line, signal line, and histogram."""
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram = macd_line - signal_line
    return pd.DataFrame(
        {"macd": macd_line, "macd_signal": signal_line, "macd_hist": histogram}
    )


def realized_volatility(
    prices: pd.Series, window: int = 20, trading_days: int = 252
) -> pd.Series:
    """Annualized realized volatility from log returns over a rolling window."""
    log_returns = np.log(prices / prices.shift(1))
    return log_returns.rolling(window=window, min_periods=window).std() * np.sqrt(trading_days)


def rolling_percentile(series: pd.Series, window: int = 252) -> pd.Series:
    """Where the current value sits within its own trailing `window`-day
    history, as a 0-1 percentile. Used for VIX percentile.
    """

    def _pct_rank(x: np.ndarray) -> float:
        return (x < x[-1]).sum() / (len(x) - 1) if len(x) > 1 else np.nan

    return series.rolling(window=window, min_periods=min(window, 60)).apply(
        _pct_rank, raw=True
    )


def build_feature_frame(
    price_df: pd.DataFrame,
    vix: pd.Series | None = None,
    price_col: str = "Close",
) -> pd.DataFrame:
    """Combine all indicators into one feature DataFrame aligned to `price_df`'s index.

    If `vix` is supplied (or a "VIX" column already exists on price_df), also
    computes VIX percentile and the IV-minus-realized-vol gap, which signals
    whether options are rich or cheap relative to recent realized moves.
    """
    prices = price_df[price_col]
    features = pd.DataFrame(index=price_df.index)

    features["sma_ratio_20"] = sma_ratio(prices, 20)
    features["sma_ratio_50"] = sma_ratio(prices, 50)
    features["bollinger_pct_b"] = bollinger_percent_b(prices, 20)
    features["momentum_10"] = momentum(prices, 10)
    features["momentum_20"] = momentum(prices, 20)
    features["rsi_14"] = rsi(prices, 14)

    macd_df = macd(prices)
    features = features.join(macd_df)

    features["realized_vol_10"] = realized_volatility(prices, 10)
    features["realized_vol_20"] = realized_volatility(prices, 20)
    features["realized_vol_60"] = realized_volatility(prices, 60)

    vix_series = vix if vix is not None else price_df.get("VIX")
    if vix_series is not None:
        vix_series = vix_series.reindex(features.index).ffill()
        features["vix"] = vix_series
        features["vix_pctile_252"] = rolling_percentile(vix_series, 252)
        # IV proxy (VIX / 100, annualized) minus realized vol: positive means
        # options are pricing in more movement than has actually occurred.
        features["iv_rv_gap_20"] = (vix_series / 100) - features["realized_vol_20"]

    return features
