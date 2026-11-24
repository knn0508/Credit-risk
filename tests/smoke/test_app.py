"""UI smoke: Streamlit AppTest, API çağırışları TestClient-ə yönləndirilir."""
import httpx
from streamlit.testing.v1 import AppTest

OK = '{"ext_source_2": 0.5, "credit_income_ratio": 2.0, "days_employed": -1000}'


def _patch(monkeypatch, client):
    def fake(method, url, **kw):
        path = url.replace("http://localhost:8000", "")
        r = client.request(method, path, json=kw.get("json"))
        return httpx.Response(r.status_code, json=r.json(), request=httpx.Request(method, url))
    monkeypatch.setattr(httpx, "request", fake)


def test_overview_and_single(client, monkeypatch):
    _patch(monkeypatch, client)
    at = AppTest.from_file("../../app/streamlit_app.py", default_timeout=20).run()
    assert not at.exception and any("DEV/MOCK" in w.value for w in at.warning)
    at.sidebar.radio[0].set_value("Single Applicant").run()
    assert any("code_gender" in c.value for c in at.caption)
    at.text_input(key="f_ext_source_2").set_value("0.5")
    at.button[0].click().run()
    assert not at.exception and any("Risk bandı" in s.value for s in at.subheader)


def test_explanation_page_without_prediction(client, monkeypatch):
    _patch(monkeypatch, client)
    at = AppTest.from_file("../../app/streamlit_app.py", default_timeout=20).run()
    at.sidebar.radio[0].set_value("Risk Explanation").run()
    assert not at.exception and at.info


def test_batch_demo_sample(client, monkeypatch):
    _patch(monkeypatch, client)
    at = AppTest.from_file("../../app/streamlit_app.py", default_timeout=30).run()
    at.sidebar.radio[0].set_value("Batch / Portfolio").run()
    at.checkbox[0].check().run()
    at.button[0].click().run()
    assert not at.exception and at.metric[0].value == "20 / 0"


def test_explanation_page_after_prediction(client, monkeypatch):
    _patch(monkeypatch, client)
    at = AppTest.from_file("../../app/streamlit_app.py", default_timeout=30).run()
    at.sidebar.radio[0].set_value("Single Applicant").run()
    at.text_input(key="f_ext_source_2").set_value("0.5")
    at.button[0].click().run()
    at.sidebar.radio[0].set_value("Risk Explanation").run()
    assert not at.exception and not at.error
    assert {"Riski artıran", "Riski azaldan"} <= {s.value for s in at.subheader}


def test_ui_shows_business_approval_warning(tmp_path, monkeypatch):
    from api.bundle import load_bundle
    from api.main import create_app
    from fastapi.testclient import TestClient
    from tests.mock.make_bundle import make_bundle
    c = TestClient(create_app(load_bundle(make_bundle(tmp_path / "bp", status="approved", business_approval="pending"))))
    _patch(monkeypatch, c)
    at = AppTest.from_file("../../app/streamlit_app.py", default_timeout=20).run()
    assert not at.exception and any("biznes təsdiqi yoxdur" in w.value for w in at.warning)


def test_demo_banner_on_every_page(client, monkeypatch):
    _patch(monkeypatch, client)
    at = AppTest.from_file("../../app/streamlit_app.py", default_timeout=30).run()
    for page in ("Overview", "Single Applicant", "Risk Explanation", "Batch / Portfolio"):
        at.sidebar.radio[0].set_value(page).run()
        assert not at.exception
        assert any("Yalnız demo/prototip; real kredit qərarları üçün deyil" in i.value for i in at.info), page
