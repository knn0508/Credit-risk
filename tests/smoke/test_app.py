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
    at.text_area[0].set_value(OK)
    at.button[0].click().run()
    assert not at.exception and any("Risk bandı" in s.value for s in at.subheader)


def test_explanation_page_without_prediction(client, monkeypatch):
    _patch(monkeypatch, client)
    at = AppTest.from_file("../../app/streamlit_app.py", default_timeout=20).run()
    at.sidebar.radio[0].set_value("Risk Explanation").run()
    assert not at.exception and at.info
