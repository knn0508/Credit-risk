# İşə salma (Agent 06)
Bundle: `artifacts/models/<model_version>/` (docs/contracts/model-bundle.md). Təsdiqsiz (`approved` olmayan) bundle yalnız `ALLOW_DEV=1` ilə, UI-da DEV xəbərdarlığı ilə.

## Lokal
    source ../../.venv/bin/activate
    BUNDLE_DIR=artifacts/models/<ver> ALLOW_DEV=1 uvicorn api.main:app --port 8000
    API_URL=http://localhost:8000 streamlit run app/streamlit_app.py
Mock bundle (yalnız DEV): `python -c "from pathlib import Path; from tests.mock.make_bundle import make_bundle; make_bundle(Path('artifacts/models/mock'))"`

## Docker
    MODEL_VERSION=<ver> ALLOW_DEV=1 docker compose -f deployment/docker-compose.yml up --build
API: :8000 (/health, /model-info, /predict, /predict/batch, /explain), UI: :8501.

## Testlər
    python -m pytest tests -q
Loglarda yalnız prediction_id, model_version, band, latency var; giriş dəyərləri yoxdur.
Sistem qərar dəstəyidir: avtomatik təsdiq/rədd yoxdur.
