"""
Two-model structure selector (phase 6 of options_strategy/PROJECT.md).

Two random forests, each checkable on its own:
  - direction model: will the underlying move up, sideways or down over the
    next `horizon` trading days, measured in units of the move the IV proxy
    implied (so a 2% move counts for more in a calm market than a wild one)
  - vol model: will realized vol over the next `horizon` days come in above
    the current IV proxy ("cheap": buying options pays) or below it ("rich":
    selling options pays)

A fixed rule table maps the pair of predictions to an options structure.

Labels are built only from the prices a signal function is handed -- in
walk-forward use, the training slice -- so the last `horizon` rows of each
label are NaN and simply drop out of training.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from options_strategy.backtester import (
    BEAR_CALL_SPREAD,
    BULL_CALL_SPREAD,
    BULL_PUT_SPREAD,
    FLAT,
    IRON_CONDOR,
    LONG_PUT,
)
from options_strategy.run_backtest import build_vol_series

BULLISH, NEUTRAL, BEARISH = "bullish", "neutral", "bearish"
CHEAP, RICH = "cheap", "rich"

RULE_TABLE = {
    (BULLISH, CHEAP): BULL_CALL_SPREAD,
    (BULLISH, RICH): BULL_PUT_SPREAD,
    (NEUTRAL, CHEAP): FLAT,
    (NEUTRAL, RICH): IRON_CONDOR,
    (BEARISH, CHEAP): LONG_PUT,
    (BEARISH, RICH): BEAR_CALL_SPREAD,
}

# Raw MACD columns are in price units and drift with the price level, so a
# tree split learned in one era doesn't transfer; macd_hist_pct replaces them.
EXCLUDED_FEATURES = ["macd", "macd_signal", "macd_hist"]


def model_features(features: pd.DataFrame) -> pd.DataFrame:
    return features.drop(columns=[c for c in EXCLUDED_FEATURES if c in features.columns])


def direction_labels(
    price_df: pd.DataFrame,
    features: pd.DataFrame,
    horizon: int = 20,
    threshold: float = 0.5,
    price_col: str = "Close",
) -> pd.Series:
    """bullish / neutral / bearish from the forward `horizon`-day return,
    scaled by the IV proxy's implied move over the same horizon. NaN where
    the forward price isn't available.
    """
    prices = price_df[price_col]
    implied_move = build_vol_series(features) * np.sqrt(horizon / 252)
    z = (prices.shift(-horizon) / prices - 1) / implied_move
    labels = pd.Series(NEUTRAL, index=prices.index, dtype=object)
    labels[z > threshold] = BULLISH
    labels[z < -threshold] = BEARISH
    labels[z.isna()] = np.nan
    return labels


def vol_labels(
    price_df: pd.DataFrame,
    features: pd.DataFrame,
    horizon: int = 20,
    price_col: str = "Close",
) -> pd.Series:
    """cheap if realized vol over the next `horizon` days exceeds today's IV
    proxy, else rich. NaN where the forward window isn't complete.
    """
    log_returns = np.log(price_df[price_col]).diff()
    # rolling(h) at t+h covers returns t+1..t+h; shift(-h) moves it back to t.
    forward_rv = log_returns.rolling(horizon).std().shift(-horizon) * np.sqrt(252)
    iv = build_vol_series(features)
    labels = pd.Series(np.where(forward_rv > iv, CHEAP, RICH), index=price_df.index, dtype=object)
    labels[forward_rv.isna() | iv.isna()] = np.nan
    return labels


def map_to_signals(direction: pd.Series, vol: pd.Series) -> pd.Series:
    return pd.Series(
        [RULE_TABLE.get((d, v), FLAT) for d, v in zip(direction, vol)], index=direction.index
    )


class TwoModelStrategy:
    """Walk-forward signal function (see walk_forward.SignalFn). Refits both
    forests on each training slice and keeps every window's test-date
    predictions in `self.predictions` so each model can be scored on its own.
    """

    def __init__(
        self,
        horizon: int = 20,
        direction_threshold: float = 0.5,
        n_estimators: int = 300,
        min_samples_leaf: int = 25,
        random_state: int = 0,
    ):
        self.horizon = horizon
        self.direction_threshold = direction_threshold
        # Big leaves: daily samples with overlapping 20-day labels are heavily
        # autocorrelated, so small leaves just memorize individual episodes.
        self.forest_params = dict(
            n_estimators=n_estimators,
            min_samples_leaf=min_samples_leaf,
            max_features="sqrt",
            random_state=random_state,
            n_jobs=-1,
        )
        self.predictions: list[pd.DataFrame] = []

    def _fit(self, X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
        rows = X.notna().all(axis=1) & y.notna()
        return RandomForestClassifier(**self.forest_params).fit(X[rows], y[rows])

    def __call__(
        self, train_features: pd.DataFrame, train_prices: pd.DataFrame, test_features: pd.DataFrame
    ) -> pd.Series:
        X_train = model_features(train_features)
        y_direction = direction_labels(
            train_prices, train_features, self.horizon, self.direction_threshold
        )
        y_vol = vol_labels(train_prices, train_features, self.horizon)
        direction_model = self._fit(X_train, y_direction)
        vol_model = self._fit(X_train, y_vol)

        X_test = model_features(test_features)
        valid = X_test.notna().all(axis=1)
        preds = pd.DataFrame(index=test_features.index, columns=["direction", "vol"], dtype=object)
        if valid.any():
            preds.loc[valid, "direction"] = direction_model.predict(X_test[valid])
            preds.loc[valid, "vol"] = vol_model.predict(X_test[valid])
        self.predictions.append(preds)

        return map_to_signals(preds["direction"], preds["vol"])