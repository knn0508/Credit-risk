import numpy as np
import pandas as pd
import pytest

from src.features import ApplicationFeatures
from src.features.application_features import DOCS, EXT, FEATURE_NAMES, REQ


def make(n=3, **over):
    d = pd.DataFrame({
        "amt_credit": [100000.0] * n, "amt_income_total": [50000.0] * n,
        "amt_annuity": [5000.0] * n, "amt_goods_price": [90000.0] * n,
        "days_birth": [-14610] * n, "days_employed": [-3652] * n,
        "cnt_fam_members": [2.0] * n, "days_registration": [-3652.5] * n,
        "days_id_publish": [-1826.25] * n,
    })
    for c in EXT:
        d[c] = 0.5
    for c in DOCS:
        d[c] = 0
    for c in REQ:
        d[c] = 1.0
    for k, v in over.items():
        d[k] = v
    return d


def test_values_and_order():
    out = ApplicationFeatures().fit(make()).transform(make())
    assert list(out.columns) == FEATURE_NAMES
    r = out.iloc[0]
    assert r.ft_credit_income_ratio == 2.0 and r.ft_credit_term == 20.0
    assert r.ft_age_years == pytest.approx(40, abs=0.01)
    assert r.ft_ext_source_prod == pytest.approx(0.125)
    assert r.ft_bureau_req_total_year == 6.0


def test_employed_anomaly_and_zero_denominator():
    d = make(days_employed=[365243, -365, -365], amt_income_total=[50000.0, 0.0, 50000.0])
    out = ApplicationFeatures().fit(d).transform(d)
    assert out.ft_employed_anom.tolist() == [1, 0, 0]
    assert np.isnan(out.ft_employed_years.iloc[0]) and np.isnan(out.ft_employed_age_ratio.iloc[0])
    assert np.isnan(out.ft_credit_income_ratio.iloc[1])


def test_all_null_ext_and_req():
    d = make()
    d[EXT] = np.nan
    d[REQ] = np.nan
    out = ApplicationFeatures().transform(d)
    assert out.ft_ext_source_mean.isna().all() and out.ft_ext_source_prod.isna().all()
    assert out.ft_bureau_req_total_year.isna().all()
    assert (out.ft_ext_source_missing_cnt == 3).all()


def test_no_target_needed_and_index_kept():
    d = make().set_index(pd.Index([10, 20, 30]))
    out = ApplicationFeatures().fit(d).transform(d)
    assert out.index.tolist() == [10, 20, 30] and "target" not in out.columns


def test_processed_contract_nan_with_flag():
    d = make(days_employed=[np.nan, -365, -365], days_employed_is_anomalous=[1, 0, 0])
    out = ApplicationFeatures().fit(d).transform(d)
    assert out.ft_employed_anom.tolist() == [1, 0, 0]
    assert np.isnan(out.ft_employed_years.iloc[0])
