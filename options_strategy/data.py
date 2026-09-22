"""
Historical market data access for the options strategy research module.

Fetches underlying price history and VIX (used as an implied-volatility proxy,
since we don't have real historical option chains) via yfinance, with a local
CSV cache so repeated backtests don't re-download the same data.

This module is read-only with respect to ~/Documents/ML4T_2026Summer -- it is
a fresh implementation, not a copy of anything there.
"""

from __future__ import annotations

import datetime as dt
from pathlib import Path

import pandas as pd
import yfinance as yf

CACHE_DIR = Path(__file__).parent / "data_cache"


def _cache_path(ticker: str, start: str, end: str) -> Path:
    safe_ticker = ticker.replace("^", "_").replace("/", "_")
    return CACHE_DIR / f"{safe_ticker}_{start}_{end}.csv"


def _download(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download OHLCV data for one ticker and normalize the columns."""
    df = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
    if df.empty:
        raise ValueError(f"No data returned for {ticker} between {start} and {end}")

    # yfinance sometimes returns MultiIndex columns (ticker, field) even for
    # a single symbol -- flatten to plain field names.
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df.index.name = "Date"
    return df


def get_price_history(
    symbol: str,
    start: str,
    end: str | None = None,
    use_cache: bool = True,
) -> pd.DataFrame:
    """Get daily OHLCV history for `symbol` between `start` and `end` (YYYY-MM-DD).

    `end` defaults to today. Results are cached to CSV under data_cache/ so
    repeated backtests over the same range don't re-hit the network.
    """
    end = end or dt.date.today().isoformat()
    cache_file = _cache_path(symbol, start, end)

    if use_cache and cache_file.exists():
        df = pd.read_csv(cache_file, index_col="Date", parse_dates=True)
        return df

    df = _download(symbol, start, end)

    if use_cache:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        df.to_csv(cache_file)

    return df


def get_vix_history(start: str, end: str | None = None, use_cache: bool = True) -> pd.Series:
    """Get daily VIX close between `start` and `end`. Used as an IV proxy
    since we don't have real historical option-chain implied vol.
    """
    df = get_price_history("^VIX", start, end, use_cache=use_cache)
    return df["Close"].rename("VIX")


def align_to_trading_days(price_df: pd.DataFrame, vix: pd.Series) -> pd.DataFrame:
    """Join underlying prices with VIX on trading-day index, forward-filling
    any VIX gaps (e.g. holidays where one series has a row and the other doesn't).
    """
    out = price_df.copy()
    out["VIX"] = vix.reindex(out.index).ffill()
    return out
