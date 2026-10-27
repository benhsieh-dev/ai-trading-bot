"""
Measure skew and bid/ask from saved chain snapshots (phase 9), in the same
form the backtester models them, and compare the backtester's structure
prices against real quotes.

Per snapshot day, using expiries between --min-days and --max-days:
  - Spot is implied from put-call parity on near-the-money strikes, which
    absorbs dividends and the 15 minutes between the stock and option
    closes. Implied vols are backed out of mid prices (Yahoo's own IV
    column is unreliable) with the backtester's rate and no dividend.
  - Skew: OTM implied vol / ATM implied vol = 1 + slope*x + curvature*x^2,
    x in standard deviations of moneyness, as in pricing.skewed_vol. Fitted
    over |x| <= --max-sd, the range the backtester's strikes fall in.
  - Bid/ask: half-spread / mid = base * (1 + mult * sd OTM), as in
    OptionsBacktester._slippage_pct.
  - VIX / ATM vol: the backtester takes VIX as ATM vol; this measures how
    far off that is at the ~30-day expiry.
  - Structures: for the expiry nearest the holding period, what the
    backtester would charge to open each candidate structure (VIX as ATM
    vol, its skew and haircut) versus real executable prices (buy at the
    ask, sell at the bid) at the nearest listed strikes.

One day of snapshots is an anecdote; the fits mean something once weeks of
days, across different vol regimes, have been saved.

Usage:
    python3 -m options_strategy.calibrate --symbol SPY
"""

from __future__ import annotations

import argparse
import math

import numpy as np
import pandas as pd
from scipy.stats import theilslopes

from options_strategy import chain_snapshots
from options_strategy.backtester import (
    BEAR_CALL_SPREAD,
    BULL_CALL_SPREAD,
    BULL_PUT_SPREAD,
    CALENDAR_DAYS_PER_YEAR,
    CASH_SECURED_PUT,
    CONTRACT_MULTIPLIER,
    IRON_CONDOR,
    LONG_CALL,
    LONG_PUT,
    OptionsBacktester,
)
from options_strategy.pricing import implied_vol
from options_strategy.run_backtest import add_pricing_args, pricing_kwargs

RATE = 0.04  # OptionsBacktester's default rate

# (quantity, option_type, strike as a multiple of spot) per structure, in
# terms of the backtester's otm_pct and spread_width_pct.
def structure_legs(otm: float, width: float) -> dict[str, list[tuple[int, str, float]]]:
    return {
        LONG_CALL: [(1, "call", 1 + otm)],
        LONG_PUT: [(1, "put", 1 - otm)],
        BULL_CALL_SPREAD: [(1, "call", 1.0), (-1, "call", 1 + width)],
        BULL_PUT_SPREAD: [(-1, "put", 1 - otm), (1, "put", 1 - otm - width)],
        BEAR_CALL_SPREAD: [(-1, "call", 1 + otm), (1, "call", 1 + otm + width)],
        IRON_CONDOR: [
            (1, "put", 1 - otm - width), (-1, "put", 1 - otm), (-1, "call", 1 + otm), (1, "call", 1 + otm + width),
        ],
        CASH_SECURED_PUT: [(-1, "put", 1 - otm)],
    }


def prepare_expiry(chain: pd.DataFrame) -> pd.DataFrame | None:
    """Implied spot, implied vols, moneyness and haircut for one expiry of
    one snapshot. Keeps OTM options (puts below the implied forward, calls
    at or above it) with a two-sided quote. None if parity can't be solved."""
    quote_time = pd.Timestamp(chain["quote_time"].iloc[0])
    expiry_close = pd.Timestamp(chain["expiry"].iloc[0]).tz_localize(quote_time.tz) + pd.Timedelta(hours=16)
    t = (expiry_close - quote_time).total_seconds() / 86400 / CALENDAR_DAYS_PER_YEAR
    if t <= 0:
        return None

    quoted = chain[(chain["bid"] > 0) & (chain["ask"] > chain["bid"])].assign(
        mid=lambda d: (d["bid"] + d["ask"]) / 2
    )
    pairs = quoted.pivot_table(index="strike", columns="option_type", values="mid").dropna()
    if pairs.empty or not {"call", "put"} <= set(pairs.columns):
        return None
    spot = chain["spot"].iloc[0]
    near = pairs.iloc[np.argsort(np.abs(pairs.index.to_numpy() - spot))[:5]]
    forward = float(np.median(near.index + math.exp(RATE * t) * (near["call"] - near["put"])))
    implied_spot = forward * math.exp(-RATE * t)

    otm = quoted[
        ((quoted["option_type"] == "put") & (quoted["strike"] < forward))
        | ((quoted["option_type"] == "call") & (quoted["strike"] >= forward))
    ].copy()
    otm["iv"] = [
        implied_vol(m, implied_spot, k, t, RATE, option_type=o)
        for m, k, o in zip(otm["mid"], otm["strike"], otm["option_type"])
    ]
    otm = otm.dropna(subset=["iv"]).sort_values("strike")
    if otm.empty:
        return None

    # ATM vol: linear interpolation of IV in log-strike at the forward.
    log_k = np.log(otm["strike"] / forward)
    atm_vol = float(np.interp(0.0, log_k, otm["iv"]))
    otm["x"] = np.log(otm["strike"] / implied_spot) / (atm_vol * math.sqrt(t))
    otm["sd_otm"] = otm["x"].abs()
    otm["iv_ratio"] = otm["iv"] / atm_vol
    otm["haircut"] = (otm["ask"] - otm["bid"]) / 2 / otm["mid"]
    return otm.assign(t=t, days=t * CALENDAR_DAYS_PER_YEAR, implied_spot=implied_spot, atm_vol=atm_vol)


def fit_skew(otm: pd.DataFrame, max_sd: float) -> tuple[float, float]:
    """Least squares iv_ratio - 1 = slope*x + curvature*x^2 (intercept fixed
    at 1, as in skewed_vol)."""
    d = otm[otm["sd_otm"] <= max_sd]
    X = np.column_stack([d["x"], d["x"] ** 2])
    (slope, curvature), *_ = np.linalg.lstsq(X, d["iv_ratio"] - 1, rcond=None)
    return float(slope), float(curvature)


def fit_haircut(otm: pd.DataFrame, max_sd: float) -> tuple[float, float]:
    """Fit haircut = base + base*mult*sd_otm through the median haircut of
    each 0.25-sd bin, with a Theil-Sen (median of pairwise slopes) line.
    Both medians because a few very cheap contracts (a $0.01 spread on a
    $0.03 call is a 17% haircut) swamp a least-squares fit, and can drag a
    whole thin bin with them. Returns (base, mult)."""
    d = otm[otm["sd_otm"] <= max_sd]
    medians = d.groupby((d["sd_otm"] // 0.25) * 0.25 + 0.125)["haircut"].median()
    if len(medians) < 3:
        return float("nan"), float("nan")
    b, a, *_ = theilslopes(medians.to_numpy(), medians.index.to_numpy())
    return float(a), float(b / a) if a > 0 else float("nan")


def compare_structures(
    chain: pd.DataFrame, otm_pct: float, width_pct: float, holding_days: int, pricing: dict
) -> pd.DataFrame:
    """Backtester open cost vs real executable open cost, per structure, at
    the expiry nearest the backtester's holding period (in calendar days).
    Positive cost = debit paid, negative = credit received; per 1 contract."""
    spot, vix = chain["spot"].iloc[0], chain["vix"].iloc[0]
    quote_time = pd.Timestamp(chain["quote_time"].iloc[0])
    date = quote_time.tz_localize(None).normalize()
    target_days = holding_days * 365 / 252
    expiry = min(
        chain["expiry"].unique(), key=lambda e: abs((pd.Timestamp(e) - date).days - target_days)
    )
    quotes = chain[(chain["expiry"] == expiry) & (chain["bid"] > 0) & (chain["ask"] > chain["bid"])]

    expiry_date = pd.Timestamp(expiry)
    bt = OptionsBacktester(
        pd.DataFrame({"Close": [spot, spot]}, index=[date, expiry_date]),
        pd.Series([vix / 100, vix / 100], index=[date, expiry_date]),
        **pricing,
    )
    t = bt._time_to_expiry(date, expiry_date)
    atm_vol = float(bt.vol.iloc[0])  # VIX after the backtester's atm_vol_scale

    rows = {}
    for name, legs in structure_legs(otm_pct, width_pct).items():
        model_cost, real_cost, strikes = 0.0, 0.0, []
        for qty, option_type, mult in legs:
            side = quotes[quotes["option_type"] == option_type]
            row = side.iloc[np.argsort(np.abs(side["strike"].to_numpy() - spot * mult))[:1]]
            if row.empty:
                break
            strike = float(row["strike"].iloc[0])
            strikes.append(strike)
            real = row["ask"].iloc[0] if qty > 0 else row["bid"].iloc[0]
            mid = bt._price_option(spot, strike, t, atm_vol, option_type)
            haircut = bt._slippage_pct(spot, strike, t, atm_vol, option_type)
            model = mid * (1 + haircut) if qty > 0 else mid * (1 - haircut)
            model_cost += qty * model * CONTRACT_MULTIPLIER
            real_cost += qty * real * CONTRACT_MULTIPLIER
        else:
            rows[name] = {
                "strikes": "/".join(f"{s:g}" for s in strikes),
                "model_cost": model_cost,
                "real_cost": real_cost,
                "model_minus_real": model_cost - real_cost,
            }
    return pd.DataFrame(rows).T.assign(expiry=expiry)


def main() -> None:
    parser = argparse.ArgumentParser(description="Calibrate skew and bid/ask from saved chain snapshots.")
    parser.add_argument("--symbol", default="SPY")
    parser.add_argument("--min-days", type=float, default=14, help="Shortest expiry to fit, calendar days")
    parser.add_argument("--max-days", type=float, default=56, help="Longest expiry to fit, calendar days")
    parser.add_argument("--max-sd", type=float, default=2.5, help="Fit strikes within this many sd of spot")
    parser.add_argument("--otm-pct", type=float, default=0.03)
    parser.add_argument("--spread-width-pct", type=float, default=0.05)
    parser.add_argument("--holding-days", type=int, default=20)
    add_pricing_args(parser)
    args = parser.parse_args()

    pricing = dict(
        otm_pct=args.otm_pct,
        spread_width_pct=args.spread_width_pct,
        holding_period_days=args.holding_days,
        **pricing_kwargs(args),
    )
    snapshots = chain_snapshots.load_snapshots(args.symbol)

    per_expiry, pooled, structures = [], [], []
    for (quote_date, expiry), chain in snapshots.groupby(["quote_date", "expiry"]):
        otm = prepare_expiry(chain)
        if otm is None or not args.min_days <= otm["days"].iloc[0] <= args.max_days:
            continue
        # Haircuts are only fitted pooled: one expiry's ~100 quotes are too
        # few for the binned fit.
        slope, curvature = fit_skew(otm, args.max_sd)
        per_expiry.append({
            "quote_date": quote_date.date(), "expiry": expiry, "days": otm["days"].iloc[0],
            "atm_vol": otm["atm_vol"].iloc[0], "vix_over_atm": chain["vix"].iloc[0] / 100 / otm["atm_vol"].iloc[0],
            "slope": slope, "curvature": curvature, "options": int((otm["sd_otm"] <= args.max_sd).sum()),
        })
        pooled.append(otm)
    for quote_date, chain in snapshots.groupby("quote_date"):
        if chain["vix"].notna().any():
            structures.append(
                compare_structures(chain, args.otm_pct, args.spread_width_pct, args.holding_days, pricing)
                .assign(quote_date=quote_date.date())
            )

    if not per_expiry:
        raise SystemExit(f"No expiries between {args.min_days} and {args.max_days} days in the snapshots")
    per_expiry = pd.DataFrame(per_expiry)
    pooled = pd.concat(pooled)
    slope, curvature = fit_skew(pooled, args.max_sd)
    base, mult = fit_haircut(pooled, args.max_sd)

    with pd.option_context("display.width", 200, "display.max_columns", None):
        days = per_expiry["quote_date"].nunique()
        print(f"{args.symbol}: {days} snapshot day(s), {len(per_expiry)} expiries "
              f"between {args.min_days:g} and {args.max_days:g} days\n")
        print("Per expiry:")
        print(per_expiry.round(4).to_string(index=False))

        print(f"\nPooled fit (|x| <= {args.max_sd:g} sd) vs backtester settings:")
        atm_vol_scale = float((1 / per_expiry["vix_over_atm"]).median())
        print(pd.DataFrame({
            "fitted": [atm_vol_scale, slope, curvature, base, mult],
            "backtester": [args.atm_vol_scale, args.skew_slope, args.skew_curvature,
                           args.option_slippage_pct, args.otm_slippage_mult],
        }, index=["atm_vol_scale", "skew_slope", "skew_curvature", "option_slippage_pct", "otm_slippage_mult"])
              .round(4).to_string())

        print("\nIV / ATM IV at 1 and 2 sd OTM, fitted vs backtester:")
        for label, (s, c) in {"fitted": (slope, curvature), "backtester": (args.skew_slope, args.skew_curvature)}.items():
            ratios = {x: 1 + s * x + c * x * x for x in (-2, -1, 1, 2)}
            print(f"  {label:<10} put 2sd {ratios[-2]:.2f}  put 1sd {ratios[-1]:.2f}  "
                  f"call 1sd {ratios[1]:.2f}  call 2sd {ratios[2]:.2f}")

        if structures:
            print("\nOpen cost per structure, backtester vs real bid/ask (1 contract; negative = credit):")
            print(pd.concat(structures).round(2).to_string())


if __name__ == "__main__":
    main()