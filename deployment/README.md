# İşə salma (Agent 06)
Sistem qərar DƏSTƏYİDİR (avtomatik təsdiq/rədd yoxdur). Bundle: `artifacts/models/<model_version>/`
(docs/contracts/model-bundle.md): model/calibrator/feature_names/metadata/risk_policy.json və `/explain` üçün
`background.parquet` (feature_names sütunları, train-dən ≤1000 sətir; yoxdursa /explain 503).

`approved` olmayan bundle yalnız `ALLOW_DEV=1` ilə yüklənir və bütün cavablarda DEV xəbərdarlığı olur.
`approved` bundle-da `excluded_protected_features` açarı məcburidir (yoxdursa yükləmə rədd edilir → 503).
Qeyd: /explain xam modelin (kalibrasiyadan əvvəl) log-odds izahıdır; göstərilən ehtimal kalibrasiya olunmuşdur.

## Təmiz mühit (lokal)
    python3.12 -m venv .venv && source .venv/bin/activate
    pip install -r requirements.txt          # və ya yalnız servis: deployment/requirements.txt
    BUNDLE_DIR=artifacts/models/<ver> ALLOW_DEV=1 uvicorn api.main:app --port 8000
    API_URL=http://localhost:8000 streamlit run app/streamlit_app.py     # ayrı terminal
Yoxlama: `curl localhost:8000/health` → `{"status":"ok","model_loaded":true}`; interaktiv sənəd: http://localhost:8000/docs
`model_loaded:false` olarsa səbəb: BUNDLE_DIR yoxdur / bundle təsdiqsizdir (ALLOW_DEV=1 lazımdır) / fayl çatışmır
(`/predict` 503 qaytarır, mesajda səbəb var).

Mock bundle (YALNIZ DEV, real model deyil):
    python -c "from pathlib import Path; from tests.mock.make_bundle import make_bundle; make_bundle(Path('artifacts/models/mock'))"
    # sonra BUNDLE_DIR=artifacts/models/mock ALLOW_DEV=1 ... (src/evaluation/risk_bands.py repo-da olmalıdır)

## Docker
    MODEL_VERSION=<ver> ALLOW_DEV=1 docker compose -f deployment/docker-compose.yml up --build
API :8000, UI :8501. Image: pinlənmiş asılılıqlar (deployment/requirements.txt), non-root (uid 10001), HEALTHCHECK /health.
Bundle və data image-ə daxil deyil. Docker build Agent 01 tərəfindən yoxlanıb (image ~1.7GB; konteyner approved bundle ilə qalxır, healthcheck healthy).

## Testlər
    python -m pytest tests -q
Loglarda yalnız prediction_id, model_version, band, latency var; giriş dəyərləri və fərdi izahlar yoxdur.
