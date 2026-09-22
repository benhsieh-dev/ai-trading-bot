"""
Options pricing: Black-Scholes price and Greeks, plus a simple IV proxy.

We don't have real historical option chains, so implied volatility here is a
proxy (VIX/100 for broad-market underlyings, or trailing realized vol as a
fallback for anything else) rather than a true market-observed IV. Every
value this module produces should be treated as a synthetic estimate, not a
historical fill price. See options_strategy/PROJECT.md for the data caveats.

No scipy dependency -- normal CDF/PDF are implemented with math.erf so this
stays within the packages already in requirements.txt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

TRADING_DAYS_PER_YEAR = 252


def norm_cdf(x: float) -> float:
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def norm_pdf(x: float) -> float:
    return math.exp(-0.5 * x * x) / math.sqrt(2 * math.pi)


def _d1_d2(
    spot: float, strike: float, time_to_expiry: float, vol: float, rate: float, dividend: float
) -> tuple[float, float]:
    if time_to_expiry <= 0 or vol <= 0:
        raise ValueError("time_to_expiry and vol must be positive")
    d1 = (
        math.log(spot / strike) + (rate - dividend + 0.5 * vol * vol) * time_to_expiry
    ) / (vol * math.sqrt(time_to_expiry))
    d2 = d1 - vol * math.sqrt(time_to_expiry)
    return d1, d2


def black_scholes_price(
    spot: float,
    strike: float,
    time_to_expiry: float,
    vol: float,
    rate: float = 0.04,
    dividend: float = 0.0,
    option_type: str = "call",
) -> float:
    """Black-Scholes price of a European call or put.

    time_to_expiry is in years (e.g. 30 / 365). vol and rate are annualized,
    decimal (0.20 = 20%). dividend is a continuous dividend yield.
    """
    option_type = option_type.lower()
    if option_type not in ("call", "put"):
        raise ValueError(f"option_type must be 'call' or 'put', got {option_type!r}")

    if time_to_expiry <= 0:
        # At/after expiry, price is intrinsic value.
        if option_type == "call":
            return max(spot - strike, 0.0)
        return max(strike - spot, 0.0)

    d1, d2 = _d1_d2(spot, strike, time_to_expiry, vol, rate, dividend)
    disc_div = math.exp(-dividend * time_to_expiry)
    disc_rate = math.exp(-rate * time_to_expiry)

    if option_type == "call":
        return spot * disc_div * norm_cdf(d1) - strike * disc_rate * norm_cdf(d2)
    return strike * disc_rate * norm_cdf(-d2) - spot * disc_div * norm_cdf(-d1)


@dataclass
class Greeks:
    delta: float
    gamma: float
    theta: float  # per calendar day
    vega: float  # per 1 vol point (1%)
    rho: float  # per 1% rate move


def black_scholes_greeks(
    spot: float,
    strike: float,
    time_to_expiry: float,
    vol: float,
    rate: float = 0.04,
    dividend: float = 0.0,
    option_type: str = "call",
) -> Greeks:
    """Greeks for a European call or put. See black_scholes_price for units."""
    option_type = option_type.lower()
    if option_type not in ("call", "put"):
        raise ValueError(f"option_type must be 'call' or 'put', got {option_type!r}")

    if time_to_expiry <= 0:
        return Greeks(delta=0.0, gamma=0.0, theta=0.0, vega=0.0, rho=0.0)

    d1, d2 = _d1_d2(spot, strike, time_to_expiry, vol, rate, dividend)
    disc_div = math.exp(-dividend * time_to_expiry)
    disc_rate = math.exp(-rate * time_to_expiry)
    sqrt_t = math.sqrt(time_to_expiry)

    gamma = disc_div * norm_pdf(d1) / (spot * vol * sqrt_t)
    vega = spot * disc_div * norm_pdf(d1) * sqrt_t / 100  # per 1 vol point

    if option_type == "call":
        delta = disc_div * norm_cdf(d1)
        theta = (
            -(spot * disc_div * norm_pdf(d1) * vol) / (2 * sqrt_t)
            - rate * strike * disc_rate * norm_cdf(d2)
            + dividend * spot * disc_div * norm_cdf(d1)
        ) / 365
        rho = strike * time_to_expiry * disc_rate * norm_cdf(d2) / 100
    else:
        delta = -disc_div * norm_cdf(-d1)
        theta = (
            -(spot * disc_div * norm_pdf(d1) * vol) / (2 * sqrt_t)
            + rate * strike * disc_rate * norm_cdf(-d2)
            - dividend * spot * disc_div * norm_cdf(-d1)
        ) / 365
        rho = -strike * time_to_expiry * disc_rate * norm_cdf(-d2) / 100

    return Greeks(delta=delta, gamma=gamma, theta=theta, vega=vega, rho=rho)


def iv_proxy_from_vix(vix_level: float) -> float:
    """Convert a VIX index level (e.g. 18.5) to an annualized vol decimal (0.185).
    Only a reasonable proxy for broad-market underlyings (SPY, QQQ, etc.).
    """
    return vix_level / 100


def iv_proxy_fallback(realized_vol: float, richness_multiplier: float = 1.1) -> float:
    """Fallback IV proxy for symbols without a VIX-like index: trailing
    realized vol scaled up slightly, since implied vol tends to run above
    realized vol on average (the variance risk premium).
    """
    return realized_vol * richness_multiplier
