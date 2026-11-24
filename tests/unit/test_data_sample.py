"""Sample schema / synthetic applicants (Agent 02 -> 06)."""
import json
from pathlib import Path

import pandas as pd
import pytest

from src.data.sample import SEED, build_input_schema, synth_applicants, to_records

P = Path("data/processed")
D = Path("docs/data")
pytestmark = pytest.mark.skipif(not (P / "schema.json").exists(), reason="run python -m src.data.build first")


@pytest.fixture(scope="module")
def ctx():
    train = pd.read_parquet(P / "application_train.parquet")
    cols = json.loads((P / "schema.json").read_text())["columns"]
    return train, build_input_schema(train, cols)


def test_schema_excludes_target_and_matches_features(ctx):
    train, fields = ctx
    names = [f["name"] for f in fields]
    assert "target" not in names and "code_gender" in names
    assert set(names) == set(train.columns) - {"target"}
    assert all(f["required"] is False for f in fields)


def test_samples_conform_to_schema(ctx):
    train, fields = ctx
    spec = {f["name"]: f for f in fields}
    recs = to_records(synth_applicants(train, fields))
    assert len(recs) == 20
    for r in recs:
        assert "target" not in r and "sk_id_curr" not in r
        for c, v in r.items():
            f = spec[c]
            if v is None:
                assert f["nullable"], f"{c} null but not nullable"
            elif "allowed_values" in f:
                assert v in f["allowed_values"], (c, v)
            else:
                assert f["min"] <= v <= f["max"], (c, v)
                if f["kind"] == "integer":
                    assert isinstance(v, int)


def test_samples_internally_consistent(ctx):
    train, fields = ctx
    for r in to_records(synth_applicants(train, fields, n=200)):
        for g in ("bureau", "previous_application", "pos_cash_balance", "credit_card_balance", "installments_payments"):
            if r[f"{g}_has_history"] == 0:
                assert all(v in (None, 0) for k, v in r.items() if k.startswith(g + "_"))
        if r["days_employed_is_anomalous"] == 1:
            assert r["days_employed"] is None


def test_samples_deterministic_and_not_real_rows(ctx):
    train, fields = ctx
    a = to_records(synth_applicants(train, fields, seed=SEED))
    assert a == to_records(synth_applicants(train, fields, seed=SEED))
    real = train.drop(columns=["target", "sk_id_curr"]).head(5000)
    key = ["amt_income_total", "amt_credit", "days_birth", "amt_annuity"]
    real_keys = set(map(tuple, real[key].to_numpy().tolist()))
    assert not any(tuple(r[k] for k in key) in real_keys for r in a)


def test_committed_artifacts_are_valid():
    sch = json.loads((D / "sample-schema.json").read_text())
    req = json.loads((D / "sample-applicants.json").read_text())
    names = {f["name"] for f in sch["fields"]}
    assert sch["n_fields"] == len(names) and "target" not in names
    assert len(req["requests"]) == 20
    for r in req["requests"]:
        assert set(r["applicant"]) <= names and "request_id" in r
