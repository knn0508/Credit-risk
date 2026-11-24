"""Data pipeline tests (Agent 02): join safety, cleaning rules, aggregation grain."""
import numpy as np
import pandas as pd
import pytest

from src.data import aggregate as A
from src.data.build import clean_application, fill_after_join, safe_left_join


def _app():
    return pd.DataFrame({
        "SK_ID_CURR": [1, 2, 3],
        "DAYS_EMPLOYED": [-100, 365243, -5],
        "CODE_GENDER": ["F", "XNA", "M"],
        "ORGANIZATION_TYPE": ["Business Entity", "XNA", "XNA"],
        "TARGET": [0, 1, 0],
    })


def test_clean_application_sentinels():
    out = clean_application(_app())
    assert out.days_employed.isna().tolist() == [False, True, False]
    assert out.days_employed_is_anomalous.tolist() == [0, 1, 0]
    assert out.code_gender.isna().tolist() == [False, True, False]
    assert out.organization_type.isna().sum() == 2
    assert all(c == c.lower() for c in out.columns)


def test_clean_application_does_not_mutate_input():
    a = _app()
    clean_application(a)
    assert (a.DAYS_EMPLOYED == 365243).sum() == 1


def test_safe_left_join_preserves_rows():
    left = clean_application(_app())
    agg = pd.DataFrame({"x": [10, 20]}, index=pd.Index([1, 3], name="sk_id_curr"))
    out = safe_left_join(left, agg)
    assert len(out) == len(left) and out.sk_id_curr.is_unique
    assert out.x.isna().tolist() == [False, True, False]


def test_safe_left_join_refuses_one_to_many():
    left = clean_application(_app())
    agg = pd.DataFrame({"x": [10, 20]}, index=pd.Index([1, 1], name="sk_id_curr"))
    with pytest.raises(AssertionError):
        safe_left_join(left, agg)


def test_installments_aggregate_unique_and_correct():
    ip = pd.DataFrame({
        "SK_ID_PREV": [1, 1, 2], "SK_ID_CURR": [7, 7, 8], "NUM_INSTALMENT_NUMBER": [1, 2, 1],
        "DAYS_INSTALMENT": [-30, -10, -20], "DAYS_ENTRY_PAYMENT": [-32, -5, -20],
        "AMT_INSTALMENT": [100.0, 100.0, 50.0], "AMT_PAYMENT": [100.0, 60.0, 50.0],
    })
    agg, lin = A.aggregate_installments(ip)
    assert agg.index.is_unique and set(agg.index) == {7, 8}
    assert agg.loc[7, "installments_payments_sk_id_prev_count"] == 2
    assert agg.loc[7, "installments_payments_is_late_sum"] == 1
    assert agg.loc[7, "installments_payments_amt_unpaid_sum"] == 40.0
    assert set(lin) == set(agg.columns)


def test_previous_application_excludes_leakage_columns():
    pa = pd.DataFrame({
        "SK_ID_PREV": [1, 2], "SK_ID_CURR": [7, 7], "NAME_CONTRACT_STATUS": ["Approved", "Refused"],
        "AMT_APPLICATION": [1.0, 2.0], "AMT_CREDIT": [1.0, 2.0], "AMT_ANNUITY": [1.0, 2.0],
        "AMT_DOWN_PAYMENT": [0.0, np.nan], "AMT_GOODS_PRICE": [1.0, 2.0], "RATE_DOWN_PAYMENT": [0.1, np.nan],
        "CNT_PAYMENT": [6.0, 12.0], "DAYS_DECISION": [-10, 365243],
        "DAYS_LAST_DUE": [1, 2], "DAYS_TERMINATION": [1, 2], "DAYS_FIRST_DRAWING": [1, 2],
        "DAYS_LAST_DUE_1ST_VERSION": [1, 2],
    })
    agg, lin = A.aggregate_previous_application(pa)
    banned = ("days_last_due", "days_termination", "days_first_drawing")
    assert not any(b in c for c in agg.columns for b in banned)
    assert agg.loc[7, "previous_application_days_decision_max"] == -10  # sentinel -> NaN, ignored
    assert agg.loc[7, "previous_application_approved_sum"] == 1


def test_bureau_balance_orphans_do_not_change_bureau_rows():
    bureau = pd.DataFrame({"SK_ID_CURR": [1, 1, 2], "SK_ID_BUREAU": [10, 11, 12],
                           "CREDIT_ACTIVE": ["Active", "Closed", "Active"], "CREDIT_TYPE": ["a", "b", "a"],
                           **{c: [0.0, 1.0, 2.0] for c in [
                               "CREDIT_DAY_OVERDUE", "DAYS_CREDIT", "DAYS_CREDIT_ENDDATE", "AMT_CREDIT_MAX_OVERDUE",
                               "CNT_CREDIT_PROLONG", "AMT_CREDIT_SUM", "AMT_CREDIT_SUM_DEBT", "AMT_CREDIT_SUM_LIMIT",
                               "AMT_CREDIT_SUM_OVERDUE", "AMT_ANNUITY"]}})
    bb = pd.DataFrame({"SK_ID_BUREAU": [10, 10, 11], "MONTHS_BALANCE": [0, -1, 0], "STATUS": ["C", "1", "X"]})
    agg, _ = A.aggregate_bureau(bureau, A.aggregate_bureau_balance(bb))
    assert agg.index.is_unique and agg.loc[1, "bureau_sk_id_bureau_count"] == 2
    assert agg.loc[1, "bureau_dpd_months_sum"] == 1
    assert np.isnan(agg.loc[2, "bureau_dpd_months_sum"])  # no balance history -> NaN, not 0


def test_fill_after_join_zero_counts_only():
    df = pd.DataFrame({"c": [1.0, np.nan], "m": [5.0, np.nan], "h": [1.0, np.nan]})
    lin = {"c": {"stat": "count"}, "m": {"stat": "mean"}, "h": {"stat": "has_history"}}
    out = fill_after_join(df, lin)
    assert out.c.tolist() == [1, 0] and out.h.tolist() == [1, 0] and out.m.isna().tolist() == [False, True]


def test_file_fingerprint_and_data_version(tmp_path):
    import hashlib
    from src.data.build import RAW_TABLES, data_version, file_fingerprint
    f = tmp_path / "x.csv"
    f.write_bytes(b"a,b\n1,2\n")
    fp = file_fingerprint(f)
    assert fp == {"bytes": 8, "sha256": hashlib.sha256(b"a,b\n1,2\n").hexdigest()}
    for t in RAW_TABLES:
        (tmp_path / f"{t}.csv").write_bytes(t.encode())
    v1 = data_version(tmp_path)
    assert len(v1["data_version"]) == 16 and set(v1["raw_files"]) == set(RAW_TABLES)
    (tmp_path / "bureau.csv").write_bytes(b"changed")
    assert data_version(tmp_path)["data_version"] != v1["data_version"]
