"""Single Applicant UI: saxta API ilə (forma quruluşu, null/boş qaydası, nümunə yükləmə)."""
import json
from pathlib import Path

import httpx
from streamlit.testing.v1 import AppTest

APP = "../../app/streamlit_app.py"
SCHEMA = {f["name"]: f for f in json.loads((Path(__file__).parents[2] / "docs/data/sample-schema.json").read_text())["fields"]}
CORE = ["ext_source_1", "ext_source_2", "ext_source_3", "amt_credit", "amt_annuity", "amt_goods_price",
        "amt_income_total", "days_birth", "days_employed", "name_education_type", "name_contract_type",
        "name_income_type", "own_car_age", "cnt_fam_members", "cnt_children"]
EXTRA = ["flag_own_car", "bureau_amt_credit_sum_sum", "apartments_avg", "amt_req_credit_bureau_year", "occupation_type"]
NAMES = CORE + EXTRA + ["ft_credit_income_ratio", "ft_age_years"]


def fake_api(monkeypatch, posts):
    info = {"model_version": "t", "algorithm": "x", "created_at": "t", "metrics": {}, "risk_policy_version": "v",
            "business_approval": "pending", "validation_status": "approved", "feature_count": len(NAMES),
            "feature_names": NAMES, "excluded_protected_features": ["code_gender"], "dev_mode": False,
            "warnings": ["Risk bandı hədləri fərziyyədir: biznes təsdiqi yoxdur"]}
    pred = {"prediction_id": "pid", "timestamp": "ts", "model_version": "t", "prediction_probability": 0.0731,
            "risk_band": "Medium", "calibrated": True, "disclaimer": "d",
            "warnings": ["200 çatışmayan sahə null qəbul edildi", "Risk bandı hədləri fərziyyədir: biznes təsdiqi yoxdur"]}

    def fake(method, url, **kw):
        path = url.replace("http://localhost:8000", "")
        if method == "POST":
            posts.append((path, kw["json"]))
        body = info if path == "/model-info" else pred
        return httpx.Response(200, json=body, request=httpx.Request(method, url))
    monkeypatch.setattr(httpx, "request", fake)


def open_single(monkeypatch):
    posts = []
    fake_api(monkeypatch, posts)
    at = AppTest.from_file(APP, default_timeout=60).run()
    at.sidebar.radio[0].set_value("Single Applicant").run()
    assert not at.exception
    return at, posts


def test_core_fields_default_extras_in_expander_and_ft_hidden(monkeypatch):
    at, _ = open_single(monkeypatch)
    assert at.expander and "Əlavə sahələr (5)" in at.expander[0].label
    in_exp = {w.key for w in at.expander[0].number_input} | {w.key for w in at.expander[0].selectbox}
    assert in_exp == {f"f_{n}" for n in EXTRA}
    keys = {w.key for w in at.number_input} | {w.key for w in at.selectbox}
    assert not any(k.startswith("f_ft_") for k in keys) and all(f"f_{n}" in keys for n in CORE)


def test_widget_types_follow_schema(monkeypatch):
    at, _ = open_single(monkeypatch)
    assert at.selectbox(key="f_name_education_type").options[1:] == [str(v) for v in SCHEMA["name_education_type"]["allowed_values"]]
    assert at.selectbox(key="f_name_education_type").value is None
    assert at.number_input(key="f_ext_source_2").value is None
    assert at.selectbox(key="f_flag_own_car").value is None


def test_empty_submit_warns_and_makes_no_request(monkeypatch):
    at, posts = open_single(monkeypatch)
    at.button[0].click().run()
    assert any("Ən azı 5 sahə doldurun (hazırda 0)" in w.value for w in at.warning) and posts == []
    at.number_input(key="f_ext_source_2").set_value(0.5)
    at.button[0].click().run()
    assert any("hazırda 1" in w.value for w in at.warning) and posts == []


def test_submit_sends_only_filled_fields_and_shows_result(monkeypatch):
    at, posts = open_single(monkeypatch)
    vals = {"ext_source_1": 0.1, "ext_source_2": 0.2, "ext_source_3": 0.3, "amt_credit": 500000.0}
    for k, v in vals.items():
        at.number_input(key=f"f_{k}").set_value(v)
    at.selectbox(key="f_name_contract_type").select("Cash loans")
    at.button[0].click().run()
    assert not at.exception and posts[-1][0] == "/predict"
    sent = posts[-1][1]["applicant"]
    assert sent == {**vals, "name_contract_type": "Cash loans"}  # null/boş göndərilmir, ft_* yoxdur
    assert {m.label: m.value for m in at.metric}["Defolt ehtimalı"] == "7.3%"
    assert any("Medium" in m.value for m in at.metric if m.label == "Risk bandı")
    assert any("biznes təsdiqi yoxdur" in w.value for w in at.warning)          # siyasət xəbərdarlığı görünür
    assert any("200 çatışmayan sahə" in c.value for c in at.caption)           # saylar qısa caption-da


def test_sample_loader_fills_form_and_clears(monkeypatch):
    at, posts = open_single(monkeypatch)
    at.selectbox(key="sample_idx").set_value(0).run()
    assert not at.exception
    sample = json.loads((Path(__file__).parents[2] / "docs/data/sample-applicants.json").read_text())["requests"][0]["applicant"]
    assert at.number_input(key="f_ext_source_2").value == sample["ext_source_2"]
    assert at.selectbox(key="f_name_education_type").value == sample["name_education_type"]
    assert at.number_input(key="f_days_birth").value == sample["days_birth"]
    at.button[0].click().run()
    assert posts and len(posts[-1][1]["applicant"]) >= 5
    assert not any(k.startswith("ft_") for k in posts[-1][1]["applicant"])
    at.selectbox(key="sample_idx").set_value(None).run()
    assert at.number_input(key="f_ext_source_2").value is None
