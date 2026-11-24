"""Contract checks on built data/processed output (skipped if not built)."""
import json
from pathlib import Path

import pandas as pd
import pytest

P = Path("data/processed")
pytestmark = pytest.mark.skipif(not (P / "schema.json").exists(), reason="run python -m src.data.build first")


@pytest.fixture(scope="module")
def frames():
    return pd.read_parquet(P / "application_train.parquet"), pd.read_parquet(P / "application_test.parquet")


def test_row_counts_and_keys(frames):
    tr, te = frames
    assert len(tr) == 307511 and len(te) == 48744
    assert tr.sk_id_curr.is_unique and te.sk_id_curr.is_unique
    assert not set(tr.sk_id_curr) & set(te.sk_id_curr)


def test_target_only_in_train(frames):
    tr, te = frames
    assert "target" in tr.columns and "target" not in te.columns
    assert set(tr.target.unique()) == {0, 1}
    assert list(tr.columns.drop("target")) == list(te.columns)


def test_no_leaky_or_sentinel_values(frames):
    tr, _ = frames
    assert not any(b in c for c in tr.columns for b in ("days_last_due", "days_termination", "days_first_drawing"))
    assert (tr.days_employed == 365243).sum() == 0
    assert "XNA" not in set(tr.code_gender.dropna()) | set(tr.organization_type.dropna())
    assert "code_gender" in tr.columns  # decisions/0002: kept for fairness audit


def test_schema_json_matches_parquet(frames):
    tr, _ = frames
    s = json.loads((P / "schema.json").read_text())
    assert [c["column"] for c in s["columns"]] == list(tr.columns)
    assert all({"dtype", "nullable", "source_table", "stat"} <= set(c) for c in s["columns"])


def test_history_flags_consistent(frames):
    tr, _ = frames
    assert tr.bureau_has_history.sum() == tr.bureau_sk_id_bureau_count.gt(0).sum()
    no_hist = tr[tr.credit_card_balance_has_history == 0]
    assert no_hist.credit_card_balance_amt_balance_mean.isna().all()
