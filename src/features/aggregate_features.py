"""Catalogue bölmə B: 02-nin SK_ID_CURR aqreqatları üzərində ratio feature-lar (stateless).
Tarixçəsizlik: mənbə aqreqat NaN -> nəticə NaN (0 ilə doldurulmur, data-contract v1.0 qərar 5).
"""
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

FEATURE_NAMES_B = [
    "ft_bureau_debt_credit_ratio", "ft_bureau_overdue_credit_ratio",
    "ft_prev_credit_application_ratio", "ft_new_credit_to_prev_credit_max",
    "ft_cc_utilization", "ft_cc_payment_balance_ratio", "ft_inst_payment_ratio",
]


def _ratio(a, b):
    return a / b.where(b > 0)


class AggregateFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        self.feature_names_ = list(FEATURE_NAMES_B)
        return self

    def get_feature_names_out(self, input_features=None):
        return np.array(FEATURE_NAMES_B, dtype=object)

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        d = X
        o = pd.DataFrame(index=d.index)
        o["ft_bureau_debt_credit_ratio"] = _ratio(d["bureau_amt_credit_sum_debt_sum"], d["bureau_amt_credit_sum_sum"])
        o["ft_bureau_overdue_credit_ratio"] = _ratio(d["bureau_amt_credit_sum_overdue_sum"], d["bureau_amt_credit_sum_sum"])
        o["ft_prev_credit_application_ratio"] = _ratio(d["previous_application_amt_credit_mean"], d["previous_application_amt_application_mean"])
        o["ft_new_credit_to_prev_credit_max"] = _ratio(d["amt_credit"], d["previous_application_amt_credit_max"])
        o["ft_cc_utilization"] = _ratio(d["credit_card_balance_amt_balance_mean"], d["credit_card_balance_amt_credit_limit_actual_mean"])
        o["ft_cc_payment_balance_ratio"] = _ratio(d["credit_card_balance_amt_payment_current_mean"], d["credit_card_balance_amt_balance_mean"])
        o["ft_inst_payment_ratio"] = _ratio(d["installments_payments_amt_payment_sum"], d["installments_payments_amt_instalment_sum"])
        return o[FEATURE_NAMES_B].astype("float64")
