"""
Daily option-chain snapshots (phase 9 of options_strategy/PROJECT.md).

Real historical chains aren't available for free, so this saves Yahoo's
chain once a day from now on. Run it after the close: Yahoo keeps the
closing bid/ask up overnight, which lines up with the daily closes the
backtester trades on. calibrate.py measures skew and bid/ask from the saved
files, to check the synthetic pricing in pricing.py and backtester.py.

Each snapshot is stored raw -- every strike of every expiry within
`max_days` calendar days, plus spot and VIX -- so later analysis can choose
its own filters. One gzipped CSV per symbol per quote date:

    options_strategy/chain_snapshots/<SYMBOL>/<YYYY-MM-DD>.csv.gz

These files can't be re-downloaded later, so back them up (or commit them).

Usage:
    python3 -m options_strategy.chain_snapshots --symbols SPY
"""

from __future__ import annotations

import argparse
import datetime as dt
from pathlib import Path
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf

SNAPSHOT_DIR = Path(__file__).parent / "chain_snapshots"
MARKET_TZ = ZoneInfo("America/New_York")

COLUMNS = [
    "contractSymbol", "lastTradeDate", "strike", "lastPrice", "bid", "ask",
    "volume", "openInterest", "impliedVolatility",
]


def snapshot_path(symbol: str, quote_date: dt.date) -> Path:
    return SNAPSHOT_DIR / symbol.upper() / f"{quote_date.isoformat()}.csv.gz"


def _vix_close() -> tuple[float, dt.date]:
    vix = yf.Ticker("^VIX").history(period="5d")
    if vix.empty:
        raise ValueError("No VIX history returned")
    return float(vix["Close"].iloc[-1]), vix.index[-1].date()


def fetch_snapshot(symbol: str, max_days: int = 70) -> tuple[pd.DataFrame, dt.date]:
    """Every call and put for expiries within `max_days` calendar days, with
    spot and VIX on each row. Returns the chain and its quote date (the
    market date of the underlying's last regular-session price)."""
    ticker = yf.Ticker(symbol)
    expiries = ticker.options
    if not expiries:
        raise ValueError(f"No option expiries returned for {symbol}")

    pieces = []
    spot, quote_time = None, None
    for expiry in expiries:
        chain = ticker.option_chain(expiry)
        if spot is None:
            spot = chain.underlying["regularMarketPrice"]
            quote_time = dt.datetime.fromtimestamp(chain.underlying["regularMarketTime"], MARKET_TZ)
        if (dt.date.fromisoformat(expiry) - quote_time.date()).days > max_days:
            break  # expiries come back sorted
        for option_type, frame in (("call", chain.calls), ("put", chain.puts)):
            frame = frame.reindex(columns=COLUMNS).assign(expiry=expiry, option_type=option_type)
            pieces.append(frame)

    vix, vix_date = _vix_close() if symbol.upper() != "^VIX" else (float("nan"), None)
    chain = pd.concat(pieces, ignore_index=True).assign(
        symbol=symbol.upper(),
        quote_time=quote_time.isoformat(),
        spot=spot,
        vix=vix if vix_date == quote_time.date() else float("nan"),
    )
    return chain, quote_time.date()


def save_snapshot(symbol: str, max_days: int = 70, force: bool = False) -> Path | None:
    """Fetch and save today's snapshot. Returns the path written, or None if
    that quote date was already saved (e.g. a rerun, or a weekend run that
    still sees Friday's quotes)."""
    chain, quote_date = fetch_snapshot(symbol, max_days)
    path = snapshot_path(symbol, quote_date)
    if path.exists() and not force:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    chain.to_csv(path, index=False, compression="gzip")
    return path


def load_snapshots(symbol: str) -> pd.DataFrame:
    """All saved snapshots for `symbol`, with a quote_date column."""
    files = sorted((SNAPSHOT_DIR / symbol.upper()).glob("*.csv.gz"))
    if not files:
        raise FileNotFoundError(f"No snapshots saved for {symbol} under {SNAPSHOT_DIR}")
    return pd.concat(
        (pd.read_csv(f).assign(quote_date=pd.Timestamp(f.name.removesuffix(".csv.gz"))) for f in files),
        ignore_index=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Save today's option-chain snapshot.")
    parser.add_argument("--symbols", nargs="+", default=["SPY"])
    parser.add_argument("--max-days", type=int, default=70, help="Furthest expiry to save, in calendar days")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing snapshot for the quote date")
    args = parser.parse_args()

    failures = 0
    for symbol in args.symbols:
        try:
            path = save_snapshot(symbol, args.max_days, args.force)
        except Exception as e:  # one bad symbol shouldn't stop the rest
            failures += 1
            print(f"{dt.datetime.now():%Y-%m-%d %H:%M} {symbol}: FAILED: {e}")
            continue
        status = f"saved {path}" if path else "already saved for this quote date, skipped"
        print(f"{dt.datetime.now():%Y-%m-%d %H:%M} {symbol}: {status}")
    raise SystemExit(1 if failures else 0)


if __name__ == "__main__":
    main()