"""Xətti modellər üçün outlier məhdudlaşdırması (ağac modellərə lazım deyil: monoton çevirməyə həssas deyillər).
STATEFUL: sərhədlər YALNIZ fit-də (train fold) öyrənilir; transform eyni sərhədlə kəsir. NaN saxlanır.
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

DEFAULT_WINSOR_COLUMNS = ["amt_income_total", "ft_income_per_person", "ft_credit_income_ratio", "ft_annuity_income_ratio"]


class Winsorizer(BaseEstimator, TransformerMixin):
    def __init__(self, columns=None, lower=0.01, upper=0.99):
        self.columns = columns
        self.lower = lower
        self.upper = upper

    def fit(self, X: pd.DataFrame, y=None):
        cols = list(self.columns) if self.columns is not None else list(DEFAULT_WINSOR_COLUMNS)
        self.columns_ = [c for c in cols if c in X.columns]
        self.bounds_ = {c: (X[c].quantile(self.lower), X[c].quantile(self.upper)) for c in self.columns_}
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        out = X.copy()
        for c, (lo, hi) in self.bounds_.items():
            out[c] = out[c].clip(lo, hi)
        return out

    def get_feature_names_out(self, input_features=None):
        return np.array(input_features, dtype=object) if input_features is not None else None
