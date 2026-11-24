"""Streamlit UI — API-nin üstündə nazik təbəqə. Başlatma: API_URL=http://localhost:8000 streamlit run app/streamlit_app.py"""
import json
import os

import httpx
import pandas as pd
import streamlit as st
import yaml

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


ROOT = os.path.join(os.path.dirname(__file__), "..")
CORE = ["ext_source_1", "ext_source_2", "ext_source_3", "amt_credit", "amt_annuity", "amt_goods_price",
        "amt_income_total", "days_birth", "days_employed", "name_education_type", "name_contract_type",
        "name_income_type", "own_car_age", "cnt_fam_members", "cnt_children"]  # SHAP top (validation report) əsaslı
MIN_FILLED = 5


@st.cache_data
def _load(rel: str):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) if p.endswith(".yaml") else json.load(f)


def _schema() -> dict:
    d = _load("docs/data/sample-schema.json")
    return {f["name"]: f for f in d["fields"]} if d else {}


def _samples() -> list:
    d = _load("docs/data/sample-applicants.json")
    return d["requests"] if d else []


def _widget(name: str, spec: dict | None, label: str):
    """Tipə uyğun widget; boş (None) = null. Giriş dəyəri yalnız bu sessiyada qalır."""
    key, kind = f"f_{name}", (spec or {}).get("kind", "float")
    hint = name
    if spec and "p01" in spec:
        hint += f" · tipik aralıq {spec['p01']:g} … {spec['p99']:g}"
    if kind == "categorical":
        return st.selectbox(label, [None] + spec["allowed_values"], key=key, help=hint,
                            format_func=lambda x: "—" if x is None else x)
    if kind == "binary":
        return st.selectbox(label, [None, 0, 1], key=key, help=hint, format_func=lambda x: "—" if x is None else str(x))
    if kind == "integer":
        return st.number_input(label, value=None, step=1, key=key, help=hint)
    return st.number_input(label, value=None, step=0.01, format="%g", key=key, help=hint)


def _coerce_sample(v, spec: dict | None):
    kind = (spec or {}).get("kind", "float")
    if v is None:
        return None
    if kind == "categorical":
        return v if v in spec["allowed_values"] else None
    if kind == "binary":
        return int(v) if v in (0, 1) else None
    try:
        return int(v) if kind == "integer" else float(v)
    except (TypeError, ValueError):
        return None


def _load_sample(fields: list[str]) -> None:
    """on_change: seçilmiş sintetik nümunə formu doldurur; '—' formu təmizləyir."""
    idx, schema, samples = st.session_state.get("sample_idx"), _schema(), _samples()
    ap = samples[idx]["applicant"] if idx is not None else {}
    for n in fields:
        st.session_state[f"f_{n}"] = _coerce_sample(ap.get(n), schema.get(n))


def _show_result(r: dict) -> None:
    with st.container(border=True):
        c1, c2 = st.columns(2)
        c1.metric("Defolt ehtimalı", f"{r['prediction_probability']:.1%}")
        c2.metric("Risk bandı", f"{COLORS.get(r['risk_band'], '')} {r['risk_band']}")
        st.caption(f"model={r['model_version']} · id={r['prediction_id']} · {r['timestamp']}")
    counts = [w for w in r["warnings"] if "çatışmayan" in w or "naməlum" in w or "törəmə" in w]
    for w in r["warnings"]:
        if w not in counts:
            st.warning(w)
    if counts:
        st.caption(" · ".join(counts))
    st.caption(r["disclaimer"])


def single():
    info = call("GET", "/model-info")
    if not info:
        return
    if info["excluded_protected_features"]:
        st.caption("Modeldən xaric edilən həssas atributlar: " + ", ".join(info["excluded_protected_features"]))
    schema, display = _schema(), _load("configs/feature_display_names.yaml") or {}
    fields = [f for f in info["feature_names"] if not f.startswith("ft_")]  # ft_* API-də avtomatik hesablanır
    core = [f for f in CORE if f in fields] or fields[:15]
    extra = [f for f in fields if f not in core]
    label = lambda n: f"{display.get(n, n)}"  # noqa: E731

    samples = _samples()
    if samples:
        st.selectbox("Nümunə yüklə (sintetik, real müraciət deyil)", [None] + list(range(len(samples))),
                     key="sample_idx", on_change=_load_sample, args=(fields,),
                     format_func=lambda i: "—" if i is None else f"Nümunə {i + 1} ({samples[i]['request_id']})")
    st.write("Əsas sahələr; boş qalan sahə çatışmayan (null) sayılır. Törəmə (ft_) göstəricilər avtomatik hesablanır.")
    with st.form("applicant"):
        cols = st.columns(3)
        for i, n in enumerate(core):
            with cols[i % 3]:
                _widget(n, schema.get(n), label(n))
        if extra:
            with st.expander(f"Əlavə sahələr ({len(extra)})"):
                cols = st.columns(3)
                for i, n in enumerate(extra):
                    with cols[i % 3]:
                        _widget(n, schema.get(n), label(n))
        go = st.form_submit_button("Qiymətləndir")
    if go:
        applicant = {n: st.session_state.get(f"f_{n}") for n in fields}
        applicant = {k: v for k, v in applicant.items() if v is not None}
        need = min(MIN_FILLED, len(fields))
        if len(applicant) < need:
            st.warning(f"Ən azı {need} sahə doldurun (hazırda {len(applicant)}).")
        else:
            r = call("POST", "/predict", json={"applicant": applicant})
            if r:
                st.session_state["last"] = (applicant, r)
    if "last" in st.session_state:
        _show_result(st.session_state["last"][1])


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
