"""validate_applicant (Agent 02 -> 06)."""
import json
from pathlib import Path

import pytest

from src.data.validate import load_schema, validate_applicant

SCHEMA = Path("docs/data/sample-schema.json")
pytestmark = pytest.mark.skipif(not SCHEMA.exists(), reason="sample-schema.json missing")


def _sample():
    return json.loads(Path("docs/data/sample-applicants.json").read_text())["requests"][0]["applicant"]


def test_all_committed_samples_are_valid():
    for r in json.loads(Path("docs/data/sample-applicants.json").read_text())["requests"]:
        res = validate_applicant(r["applicant"])
        assert res.ok, res.errors
        assert set(res.cleaned) == set(load_schema())


def test_missing_and_unknown_are_warnings():
    a = _sample()
    del a["amt_credit"]
    a["target"] = 1
    res = validate_applicant(a)
    assert res.ok and res.cleaned["amt_credit"] is None and "target" not in res.cleaned
    assert any("amt_credit" in w for w in res.warnings) and any("unknown field ignored: target" in w for w in res.warnings)


@pytest.mark.parametrize("field,value", [
    ("amt_credit", "1000"), ("amt_credit", True), ("amt_credit", float("nan")), ("amt_credit", float("inf")),
    ("cnt_children", 1.5), ("flag_own_car", 1), ("name_contract_type", "Nonexistent"),
    ("flag_document_3", 2), ("flag_document_3", True), ("code_gender", ["M"]),
])
def test_type_and_allowed_value_errors(field, value):
    a = _sample()
    a[field] = value
    res = validate_applicant(a)
    assert not res.ok and any(e.startswith(field) for e in res.errors)


def test_out_of_range_is_only_a_warning_and_errors_hide_values():
    a = _sample()
    a["amt_income_total"] = 10 ** 12
    a["name_income_type"] = "SECRET-VALUE-123"
    res = validate_applicant(a)
    assert any("amt_income_total" in w for w in res.warnings)
    assert any(e.startswith("name_income_type") for e in res.errors)
    assert "SECRET-VALUE-123" not in " ".join(res.errors + res.warnings)


def test_non_object_input():
    assert not validate_applicant([1, 2]).ok
