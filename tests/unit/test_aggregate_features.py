import json
import numpy as np
import pandas as pd
import pytest

from src.features import AggregateFeatures
from src.features.aggregate_features import FEATURE_NAMES_B

COLS = ["bureau_amt_credit_sum_debt_sum", "bureau_amt_credit_sum_overdue_sum", "bureau_amt_credit_sum_sum",
        "previous_application_amt_credit_mean", "previous_application_amt_application_mean",
        "previous_application_amt_credit_max", "amt_credit", "credit_card_balance_amt_balance_mean",
        "credit_card_balance_amt_credit_limit_actual_mean", "credit_card_balance_amt_payment_current_mean",
        "installments_payments_amt_payment_sum", "installments_payments_amt_instalment_sum"]


def test_values_order_and_nohistory_nan():
    d = pd.DataFrame(1.0, index=[5, 6], columns=COLS)
    d.loc[6] = np.nan
    d.loc[6, "amt_credit"] = 100.0
    out = AggregateFeatures().fit(d).transform(d)
    assert list(out.columns) == FEATURE_NAMES_B
    assert (out.loc[5] == 1.0).all()
    assert out.loc[6].isna().all() and out.index.tolist() == [5, 6]


def test_zero_denominator_nan():
    d = pd.DataFrame(1.0, index=[0], columns=COLS)
    d["bureau_amt_credit_sum_sum"] = 0.0
    assert np.isnan(AggregateFeatures().transform(d).ft_bureau_debt_credit_ratio.iloc[0])


def test_columns_exist_in_schema():
    try:
        cols = {c["column"] for c in json.load(open("data/processed/schema.json"))["columns"]}
    except FileNotFoundError:
        pytest.skip("processed schema yoxdur")
    assert set(COLS) <= cols
