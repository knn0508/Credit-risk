"""Streamlit UI — API-nin üstündə nazik təbəqə. Başlatma: API_URL=http://localhost:8000 streamlit run app/streamlit_app.py"""
import json
import os

import httpx
import pandas as pd
import streamlit as st

API = os.environ.get("API_URL", "http://localhost:8000")
DISCLAIMER = ("Qərar dəstəyidir; avtomatik təsdiq/rədd deyil. Yalnız demo/prototip; real kredit qərarları üçün deyil. SHAP model davranışını izah edir, səbəb-nəticə sübutu deyil.")
COLORS = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}


def call(method: str, path: str, **kw):
    try:
        r = httpx.request(method, API + path, timeout=60, **kw)
    except httpx.HTTPError as e:
        st.error(f"API əlçatan deyil: {type(e).__name__}")
        return None
    if r.status_code != 200:
        st.error(f"API xətası {r.status_code}: {r.json().get('detail', r.text)[:300]}")
        return None
    return r.json()


def banner(info: dict) -> None:
    if info.get("dev_mode"):
        st.warning(f"DEV/MOCK rejimi: model təsdiqlənməyib (status={info['validation_status']}). Nəticələr real qərar üçün deyil.")
    for w in info.get("warnings", []):
        st.warning(w)
    st.caption(DISCLAIMER)


def overview():
    info = call("GET", "/model-info")
    if info:
        banner(info)
        c1, c2, c3 = st.columns(3)
        c1.metric("Model", info["model_version"])
        c2.metric("Status", info["validation_status"])
        c3.metric("Feature sayı", info["feature_count"])
        st.write({k: info[k] for k in ("algorithm", "created_at", "risk_policy_version")})
        st.subheader("Metrikalar")
        st.table(pd.DataFrame(info["metrics"].items(), columns=["metrik", "dəyər"]))


def single():
    info = call("GET", "/model-info")
    if not info:
        return
    if info["excluded_protected_features"]:
        st.caption("Modeldən xaric edilən həssas atributlar: " + ", ".join(info["excluded_protected_features"]))
    st.write("Bilinən dəyərləri daxil edin; boş qalan sahə çatışmayan (null) sayılır.")
    applicant = {}
    with st.form("applicant"):
        cols = st.columns(3)
        for i, name in enumerate(info["feature_names"]):
            raw = cols[i % 3].text_input(name, key=f"f_{name}")
            if raw.strip():
                try:
                    applicant[name] = float(raw)
                except ValueError:
                    applicant[name] = raw.strip()
        go = st.form_submit_button("Qiymətləndir")
    if go:
        r = call("POST", "/predict", json={"applicant": applicant})
        if r:
            st.session_state["last"] = (applicant, r)
    if "last" in st.session_state:
        _, r = st.session_state["last"]
        st.metric("Defolt ehtimalı", f"{r['prediction_probability']:.1%}")
        st.subheader(f"{COLORS.get(r['risk_band'], '')} Risk bandı: {r['risk_band']}")
        st.caption(f"model={r['model_version']} · id={r['prediction_id']} · {r['timestamp']}")
        for w in r["warnings"]:
            st.warning(w)
        st.caption(r["disclaimer"])


def explanation():
    if "last" not in st.session_state:
        st.info("Əvvəl 'Single Applicant' səhifəsində qiymətləndirmə edin.")
        return
    applicant, _ = st.session_state["last"]
    top_n = st.slider("Top N", 1, 10, 5)
    show = st.checkbox("Dəyərləri göstər (həssas ola bilər)", False)
    e = call("POST", f"/explain?top_n={top_n}&include_values={str(show).lower()}", json={"applicant": applicant})
    if e:
        x = e["explanation"]
        st.caption(f"{x['method']} · fəza: {x['explanation_space']}")
        for title, key in (("Riski artıran", "top_positive_factors"), ("Riski azaldan", "top_negative_factors")):
            st.subheader(title)
            st.dataframe(pd.DataFrame(x[key]), hide_index=True)
        st.caption(x["note"])


SAMPLE = os.path.join(os.path.dirname(__file__), "..", "docs", "data", "sample-applicants.json")


def batch():
    f = st.file_uploader("CSV (sütunlar = feature_name)", type="csv")
    demo = st.checkbox("Sintetik demo nümunəsi istifadə et (real müraciət deyil)")
    if (f or demo) and st.button("Skorla"):
        if demo:
            with open(SAMPLE, encoding="utf-8") as fh:
                df = pd.DataFrame([r["applicant"] for r in json.load(fh)["requests"]])
        else:
            df = pd.read_csv(f)
        if len(df) > 10_000:
            st.error("Maksimum 10 000 sətir")
            return
        rows = json.loads(df.to_json(orient="records"))  # NaN → null
        r = call("POST", "/predict/batch", json={"applicants": rows})
        if r:
            s = r["summary"]
            st.metric("Uğurlu / xəta", f"{s['ok']} / {s['failed']}")
            ok = [{"index": x["index"], **{k: x["prediction"][k] for k in ("prediction_probability", "risk_band")}}
                  for x in r["results"] if x["status"] == "ok"]
            if ok:
                out = pd.DataFrame(ok)
                st.bar_chart(out["risk_band"].value_counts())
                st.dataframe(out, hide_index=True)
                st.download_button("CSV yüklə", out.to_csv(index=False), "scores.csv")
            bad = [(x["index"], x["error"]["code"]) for x in r["results"] if x["status"] == "error"]
            if bad:
                st.warning(f"Xəta sətirləri: {bad[:20]}")


PAGES = {"Overview": overview, "Single Applicant": single, "Risk Explanation": explanation, "Batch / Portfolio": batch}
st.set_page_config(page_title="Credit Risk Decision Support", layout="wide")
st.title("Credit Risk — Qərar Dəstəyi")
st.info("Yalnız demo/prototip; real kredit qərarları üçün deyil. Qərar dəstəyidir: avtomatik təsdiq/rədd yoxdur.")  # hər səhifədə
PAGES[st.sidebar.radio("Səhifə", list(PAGES))]()
