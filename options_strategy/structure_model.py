"""
Structure-P&L selector (phase 7 of options_strategy/PROJECT.md).

Phase 6 predicts direction and vol and maps them to a structure through a
fixed rule table. This model skips the rule table and learns each
structure's payoff directly: for every training day, open each candidate
structure, hold it `horizon` trading days with the backtester's own pricing
(skew, slippage, commissions), and use its return on capital at risk as a
regression label. One random forest per structure predicts that return on
test days; the structure with the highest prediction is traded, or nothing
if none clears `min_edge`.

Return on capital at risk = P&L / max(open cost, max loss), the cash the
backtester requires before it opens a structure. That puts a condor taking
in $300 with $1,700 at risk and a $400 debit spread on the same scale.

Labels are built only from the prices a signal function is handed -- in
walk-forward use, the training slice -- so the last `horizon` days have no
exit price and drop out of training.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from options_strategy.backtester import (
    BEAR_CALL_SPREAD,
    BULL_CALL_SPREAD,
    BULL_PUT_SPREAD,
    CASH_SECURED_PUT,
    FLAT,
    IRON_CONDOR,
    LONG_CALL,
    LONG_PUT,
    OptionsBacktester,
)
from options_strategy.models import model_features
from options_strategy.run_backtest import build_vol_series

# Covered call and protective put are left out: their stock leg ties up the
# full share price, so they behave like a stock position more than an
# options trade and wouldn't be comparable to phase 6.
CANDIDATES = (
    LONG_CALL,
    LONG_PUT,
    BULL_CALL_SPREAD,
    BULL_PUT_SPREAD,
    BEAR_CALL_SPREAD,
    IRON_CONDOR,
    CASH_SECURED_PUT,
)


def structure_returns(
    price_df: pd.DataFrame,
    features: pd.DataFrame,
    structures: tuple[str, ...] = CANDIDATES,
    horizon: int = 20,
    **backtester_kwargs,
) -> pd.DataFrame:
    """Return on capital at risk of opening each structure on each day and
    holding it `horizon` trading days. One column per structure; NaN where
    the structure can't be built or the exit day is past the end of
    `price_df`. `backtester_kwargs` (otm_pct, skew, slippage, ...) must match
    the backtest the signals will be scored in.
    """
    backtester = OptionsBacktester(
        price_df, build_vol_series(features), holding_period_days=horizon, **backtester_kwargs
    )
    returns = {}
    for structure in structures:
        column = []
        for idx in range(len(price_df)):
            trade = backtester.trade_outcome(structure, idx)
            column.append(np.nan if trade is None else trade.pnl / max(trade.entry_cost, trade.max_loss))
        returns[structure] = column
    return pd.DataFrame(returns, index=price_df.index)


def choose_structures(expected: pd.DataFrame, min_edge: float = 0.0) -> pd.Series:
    """Per row, the column with the highest expected return, or FLAT if no
    column beats `min_edge` or the row has missing values."""
    signals = pd.Series(FLAT, index=expected.index, dtype=object)
    valid = expected.notna().all(axis=1)
    if valid.any():
        best = expected[valid].astype(float).idxmax(axis=1)
        clears = expected[valid].max(axis=1) > min_edge
        signals[best[clears].index] = best[clears]
    return signals


class StructurePnLStrategy:
    """Walk-forward signal function (see walk_forward.SignalFn). Refits one
    forest per candidate structure on each training slice. Keeps every
    window's test-date predictions in `self.predictions`, and the training
    slice's mean return per structure (the naive forecast the forests have
    to beat) in `self.training_means`, both indexed by test date.
    """

    def __init__(
        self,
        horizon: int = 20,
        min_edge: float = 0.0,
        structures: tuple[str, ...] = CANDIDATES,
        n_estimators: int = 300,
        min_samples_leaf: int = 25,
        random_state: int = 0,
        **backtester_kwargs,
    ):
        self.horizon = horizon
        self.min_edge = min_edge
        self.structures = structures
        self.backtester_kwargs = backtester_kwargs
        # Same forest settings as phase 6: big leaves because overlapping
        # 20-day labels make neighboring daily samples nearly duplicates.
        self.forest_params = dict(
            n_estimators=n_estimators,
            min_samples_leaf=min_samples_leaf,
            max_features="sqrt",
            random_state=random_state,
            n_jobs=-1,
        )
        self.predictions: list[pd.DataFrame] = []
        self.training_means: list[pd.DataFrame] = []

    def __call__(
        self, train_features: pd.DataFrame, train_prices: pd.DataFrame, test_features: pd.DataFrame
    ) -> pd.Series:
        y_train = structure_returns(
            train_prices, train_features, self.structures, self.horizon, **self.backtester_kwargs
        )
        X_train = model_features(train_features)
        X_test = model_features(test_features)
        valid = X_test.notna().all(axis=1)

        preds = pd.DataFrame(index=test_features.index, columns=list(self.structures), dtype=float)
        for structure in self.structures:
            rows = X_train.notna().all(axis=1) & y_train[structure].notna()
            forest = RandomForestRegressor(**self.forest_params).fit(X_train[rows], y_train[structure][rows])
            if valid.any():
                preds.loc[valid, structure] = forest.predict(X_test[valid])
        self.predictions.append(preds)
        self.training_means.append(
            pd.DataFrame([y_train.mean()] * len(test_features), index=test_features.index)
        )
        return choose_structures(preds, self.min_edge)


class BestAverageStrategy:
    """Naive benchmark: trade whichever structure had the highest mean return
    on the training slice, every test day (FLAT if none beats `min_edge`).
    The structure model has to beat this to show its features add anything.
    """

    def __init__(
        self,
        horizon: int = 20,
        min_edge: float = 0.0,
        structures: tuple[str, ...] = CANDIDATES,
        **backtester_kwargs,
    ):
        self.horizon = horizon
        self.min_edge = min_edge
        self.structures = structures
        self.backtester_kwargs = backtester_kwargs
        self.picks: list[str] = []

    def __call__(
        self, train_features: pd.DataFrame, train_prices: pd.DataFrame, test_features: pd.DataFrame
    ) -> pd.Series:
        y_train = structure_returns(
            train_prices, train_features, self.structures, self.horizon, **self.backtester_kwargs
        )
        means = y_train.mean()
        pick = means.idxmax() if means.max() > self.min_edge else FLAT
        self.picks.append(pick)
        return pd.Series(pick, index=test_features.index, dtype=object)
