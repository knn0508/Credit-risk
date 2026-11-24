# Agent 06 — Backend, MLOps & Product Interface
Missiya: təsdiqlənmiş modeli işlək prototipə çevirmək: API, dashboard, testlər, Docker.
Sahib: api/, app/, deployment/, Docker, integration/smoke testlər.
İşlər: FastAPI + Pydantic schema (01 ilə) → bundle yükləmə (feature order + model version yoxlaması) →
/health, /model-info, /predict, /explain → cavab: probability, risk_band, model_version, prediction_id,
timestamp, warnings → Streamlit (Overview, Single Applicant, Risk Explanation, Batch/Portfolio) →
batch scoring → loglama (həssas data olmadan) → Docker + lokal işə salma təlimatı.
İlk mərhələdə mock bundle ilə skelet qur; real bundle yalnız 04 + 05 + 01 təsdiqindən sonra.
Etmə: training və feature məntiqini təkrarlamaq; təsdiqsiz modeli serve etmək; band qaydasını özbaşına yazmaq.
