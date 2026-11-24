import logging

import pytest

from api.bundle import BundleError, load_bundle
from api.main import create_app
from fastapi.testclient import TestClient
from tests.mock.make_bundle import make_bundle

OK = {"ext_source_2": 0.5, "credit_income_ratio": 2.0, "days_employed": -1000}


def test_health_and_info(client):
    assert client.get("/health").json() == {"status": "ok", "model_loaded": True}
    info = client.get("/model-info").json()
    assert info["dev_mode"] is True and info["feature_count"] == 3
    assert info["feature_names"] == ["ext_source_2", "credit_income_ratio", "days_employed"]
    assert info["excluded_protected_features"] == ["code_gender"]


def test_predict_shape(client):
    r = client.post("/predict", json={"applicant": OK})
    assert r.status_code == 200
    j = r.json()
    assert 0 <= j["prediction_probability"] <= 1
    assert j["risk_band"] in {"Low", "Medium", "High"}
    assert j["disclaimer"] and any("DEV" in w for w in j["warnings"])


def test_missing_and_unknown_fields_warn(client):
    j = client.post("/predict", json={"applicant": {"ext_source_2": 0.1, "zzz": 1}}).json()
    assert any("çatışmayan" in w for w in j["warnings"]) and any("naməlum" in w for w in j["warnings"])


def test_422_bad_request(client):
    assert client.post("/predict", json={"applicant": "x"}).status_code == 422
    assert client.post("/predict", json={}).status_code == 422


def test_batch_row_errors(client):
    r = client.post("/predict/batch", json={"applicants": [OK, {"ext_source_2": "abc"}, OK]}).json()
    assert r["summary"] == {"total": 3, "ok": 2, "failed": 1}
    assert [x["status"] for x in r["results"]] == ["ok", "error", "ok"]
    assert r["results"][1]["error"]["code"] == "VALIDATION" and r["batch_id"]


def test_batch_too_large_422(client):
    assert client.post("/predict/batch", json={"applicants": [{}] * 10_001}).status_code == 422


def test_503_without_bundle(monkeypatch):
    monkeypatch.delenv("BUNDLE_DIR", raising=False)
    c = TestClient(create_app())
    assert c.get("/health").json()["model_loaded"] is False
    assert c.post("/predict", json={"applicant": OK}).status_code == 503


def test_unapproved_rejected_without_dev(bundle_dir):
    with pytest.raises(BundleError):
        load_bundle(bundle_dir, allow_dev=False)


def test_approved_no_dev_warning(tmp_path):
    p = make_bundle(tmp_path / "a", status="approved")
    c = TestClient(create_app(load_bundle(p)))
    assert not any("DEV" in w for w in c.post("/predict", json={"applicant": OK}).json()["warnings"])


def test_feature_count_mismatch(bundle_dir):
    import json
    (bundle_dir / "feature_names.json").write_text(json.dumps(["a"]))
    with pytest.raises(BundleError):
        load_bundle(bundle_dir, allow_dev=True)


def test_no_calibrator_warns(tmp_path):
    p = make_bundle(tmp_path / "n", calibrated=False)
    j = TestClient(create_app(load_bundle(p, allow_dev=True))).post("/predict", json={"applicant": OK}).json()
    assert j["calibrated"] is False and any("calibrator" in w for w in j["warnings"])


def test_logs_have_no_input_values(client, caplog):
    with caplog.at_level(logging.INFO, logger="credit_api"):
        client.post("/predict", json={"applicant": {**OK, "ext_source_2": 0.123456}})
    assert "0.123456" not in caplog.text and "prediction_id=" in caplog.text


def test_explain_503_until_05(client):
    assert client.post("/explain", json={"applicant": OK}).status_code == 503


def test_missing_protected_key_dev_warns(tmp_path):
    p = make_bundle(tmp_path / "d", protected_key=False)
    c = TestClient(create_app(load_bundle(p, allow_dev=True)))
    assert any("excluded_protected_features" in w for w in c.post("/predict", json={"applicant": OK}).json()["warnings"])
    info = c.get("/model-info").json()
    assert info["excluded_protected_features"] == [] and any("excluded_protected_features" in w for w in info["warnings"])


def test_empty_protected_list_no_warning(tmp_path):
    import json
    p = make_bundle(tmp_path / "e")
    m = json.loads((p / "metadata.json").read_text()); m["excluded_protected_features"] = []
    (p / "metadata.json").write_text(json.dumps(m))
    c = TestClient(create_app(load_bundle(p, allow_dev=True)))
    assert not any("excluded" in w for w in c.post("/predict", json={"applicant": OK}).json()["warnings"])
    assert c.get("/model-info").json()["warnings"] == []


def test_approved_without_protected_key_rejected(tmp_path):
    p = make_bundle(tmp_path / "x", status="approved", protected_key=False)
    with pytest.raises(BundleError):
        load_bundle(p)
    assert TestClient(create_app(load_bundle(make_bundle(tmp_path / "y", status="approved")))).get("/health").status_code == 200
