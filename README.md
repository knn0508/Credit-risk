# Intelligent Credit Risk Assessment Platform

Home Credit Default Risk datasetı üzərində kredit müraciətinin **defolt ehtimalını** qiymətləndirən, nəticəni
**Low / Medium / High** risk bandına çevirən, **SHAP** ilə izah verən və kredit mütəxəssisinə **qərar dəstəyi**
göstərən ML prototipi.

> **Status: yalnız demo/prototip.** Sistem avtomatik kredit təsdiqi/rədd qərarı VERMİR və real kredit qərarları üçün
> nəzərdə tutulmayıb. Risk hədləri biznes təsdiqi olmayan **fərziyyədir**. Real istifadədən əvvəl hüquqi və biznes baxışı
> məcburidir (bax [`docs/decisions/0004-business-legal-review.md`](docs/decisions/0004-business-legal-review.md)).

## Nəticələr (seçilmiş model `xgb-20261124-a9b6c81`)

| Göstərici | Dəyər |
|---|---|
| Model | XGBoost, 242 feature, Platt kalibrasiya, seed 42 |
| Holdout ROC-AUC / PR-AUC | 0.790 (CI 0.783–0.797) / 0.290 (baza 0.081) |
| Brier / ECE (holdout) | 0.0655 / 0.0021 |

| Band (hədlər fərziyyədir) | Holdout payı | Defolt dərəcəsi |
|---|---|---|
| Low (p ≤ 0.0274) | 30.0% | 1.5% |
| Medium | 60.1% | 7.6% |
| High (p > 0.1915) | 9.9% | 30.8% |

Tam hesabat: [`reports/validation_report_xgb-20261124-a9b6c81.md`](reports/validation_report_xgb-20261124-a9b6c81.md),
model card: [`reports/model_card_xgb-20261124-a9b6c81.md`](reports/model_card_xgb-20261124-a9b6c81.md).
Fairness audit statistikdir və ədalətlilik sübutu deyil; yaş, cins-proksi və region üzrə məlum fərqlər sənədləşib.

## Arxitektura

```
data/raw (Kaggle CSV)
   │  src/data          — audit, 6 köməkçi cədvəlin SK_ID_CURR-ə aqreqasiyası, validasiya
   ▼
data/processed/*.parquet + schema.json (data_version)
   │  src/features      — 23 ft_ feature (train və inference EYNİ kod)
   ▼
src/models              — protokol, baseline/benchmark, tuning, model bundle
   ▼
artifacts/models/<version>/   (Git-ə girmir)
   │  src/evaluation, src/explainability — OOF kalibrasiya, hədlər, holdout, SHAP, fairness
   ▼
api/ (FastAPI)  ◄──  app/ (Streamlit)  ·  deployment/ (Docker)
```

Əsas qaydalar: data leakage yoxdur; `application_test` model/hədd seçimində istifadə olunmur; fit yalnız train fold-da;
kalibrasiya və hədlər OOF-da seçilir, holdout yalnız son hesabatda bir dəfə işlədilir.

## Repo strukturu

| Yol | Məzmun |
|---|---|
| `src/data/` | inventar, audit, aqreqasiya, `build`, drift, tək-müraciət validasiyası |
| `src/features/` | `ApplicationFeatures`, `AggregateFeatures`, `Winsorizer` |
| `src/models/` | protokol (split/CV), baseline, benchmark, tuning, bundle |
| `src/evaluation/`, `src/explainability/` | metrik, kalibrasiya, hədlər, risk bandı, subgroup audit, SHAP |
| `api/`, `app/`, `deployment/` | FastAPI, Streamlit, Dockerfile və compose |
| `configs/` | `data.yaml`, `training.yaml`, `risk_policy.yaml`, `feature_display_names.yaml` |
| `docs/contracts/` | data, model bundle, API və izah kontraktları |
| `docs/decisions/` | qərar qeydləri 0001–0004 |
| `docs/data/`, `docs/features/` | data dictionary, keyfiyyət və drift hesabatı, feature catalogue |
| `reports/` | validasiya, fairness, model card, OOF/holdout nəticələri |
| `tests/` | unit, evaluation, integration, smoke testlər |
| `data/`, `artifacts/` | Git-ə girmir (raw data, processed data, model bundle-ları) |

## Quraşdırma

Python 3.12 lazımdır.

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Kaggle Home Credit fayllarını `data/raw/` qovluğuna qoyun (`application_train.csv`, `application_test.csv`,
`bureau.csv`, `bureau_balance.csv`, `previous_application.csv`, `POS_CASH_balance.csv`,
`credit_card_balance.csv`, `installments_payments.csv`). Raw data və model faylları Git-ə daxil edilmir.

## Pipeline-ı işlətmək

```bash
# 1. Data: data/processed/*.parquet və schema.json (deterministikdir, data_version qeyd olunur)
python -m src.data.build

# 2. Modelləşdirmə (protokol configs/training.yaml-dadır; seed 42, 80/20 split, 5-fold CV)
python -m src.models.train_baseline --model logreg
python -m src.models.benchmark --models xgb --save      # bundle yazır: artifacts/models/<version>/
python -m src.models.tune                                # tuning nəticəsi artifacts/models/tuning_results.json

# 3. Validasiya (05): OOF kalibrasiya və hədd təklifi, sonra holdout (bir dəfə)
python -m src.evaluation.run_oof     artifacts/models/<version>
python -m src.evaluation.run_holdout artifacts/models/<version>
python -m src.evaluation.run_audit   artifacts/models/<version> <low_max> <medium_max> oof
```

XGBoost və CatBoost GPU-da işləyə bilər (`device: auto`, CPU fallback var); LightGBM və LogReg CPU-dadır.
GPU nəticələri bit-bit təkrarlanmaya bilər; cihaz və kitabxana versiyaları bundle metadata-sında qeyd olunur.

**Bundle statusları:** `unvalidated` (04) → `validated` (05) → `approved` (01, `risk_policy.json` ilə). Təsdiqləmə
addımı əl ilə aparılır və repo-da skript kimi yoxdur; qaydalar [`docs/contracts/model-bundle.md`](docs/contracts/model-bundle.md)-dədir.
`approved` olmayan bundle API-də yalnız `ALLOW_DEV=1` ilə yüklənir.

## API və UI

```bash
# API
BUNDLE_DIR=artifacts/models/<version> uvicorn api.main:app --port 8000
# UI (ayrı terminal)
API_URL=http://localhost:8000 streamlit run app/streamlit_app.py
```

| Endpoint | Təyinat |
|---|---|
| `GET /health` | servis və bundle vəziyyəti |
| `GET /model-info` | model versiyası, metriklər, feature siyahısı, xəbərdarlıqlar |
| `POST /predict` | ehtimal, risk bandı, `prediction_id`, xəbərdarlıqlar, disclaimer |
| `POST /explain` | `/predict` + SHAP faktorları (`include_values`, `top_n` parametrləri) |
| `POST /predict/batch` | sətir-səviyyəli xəta ilə toplu qiymətləndirmə |

Interaktiv sənəd: `http://localhost:8000/docs`. Törəmə `ft_*` feature-ları sorğuda göndərmək lazım deyil: API onları
train ilə eyni `src/features` kodundan hesablayır. Loglarda giriş dəyərləri və fərdi izahlar yoxdur.
Streamlit səhifələri: Overview, Single Applicant, Risk Explanation, Batch / Portfolio.

Nümunə sorğular (sintetik, real sətir yoxdur): [`docs/data/sample-applicants.json`](docs/data/sample-applicants.json).

## Docker

```bash
MODEL_VERSION=<version> docker compose -f deployment/docker-compose.yml up --build
```

API `:8000`, UI `:8501`. Image pinlənmiş asılılıqlarla qurulur (`deployment/requirements.txt`, CPU-only), non-root işləyir,
healthcheck var. Bundle image-ə daxil deyil, read-only volume kimi qoşulur. Ətraflı: [`deployment/README.md`](deployment/README.md).

## Testlər

```bash
python -m pytest -q
```

Son yoxlamada 139 test keçib. Yoxlanmayanlar: modelin yenidən train ilə təkrarlanması və Streamlit UI-nin real
brauzerdə yoxlanması (UI yalnız Streamlit `AppTest` ilə test olunub).

## Əsas qərarlar

| Qərar | Məzmun |
|---|---|
| [0001](docs/decisions/0001-split-seed-threshold.md) | split, seed, hədd yanaşması, kitabxanalar |
| [0002](docs/decisions/0002-protected-attributes.md) | `code_gender` modeldən xaric (yalnız audit), yaş qalır və audit olunur |
| [0003](docs/decisions/0003-bureau-balance-coverage.md) | `bureau_balance` törəmə sütunları xaric (train 35% / test 100% əhatə sürüşməsi) |
| [0004](docs/decisions/0004-business-legal-review.md) | yalnız demo/prototip, Aİ çərçivəsi (GDPR / AI Act), hədlər fərziyyə |

## Məlum məhdudiyyətlər

- Zaman sütunu yoxdur: zaman əsaslı validasiya mümkün deyil; train/test paylanma sürüşməsi məlumdur (`docs/data/drift-report.md`).
- Cost matrix (FN:FP) fərziyyədir; hədlər və band payları biznes tutumu ilə uzlaşdırılmayıb.
- Model `<30` və `60+` yaş qrupları arasında real defolt fərqindən böyük band fərqi yaradır; yaşı çıxarmaq bunu azaltmır.
- SHAP model davranışını izah edir, səbəb-nəticə sübutu deyil.
- Data mənbəyi Kaggle Home Credit-dir; real məqsəd üçün lisenziya şərtləri yoxlanmalıdır.

## Necə işlənib

Layihə altı agent tərəfindən paralel hazırlanıb (orchestrator, data, features, modeling, validation, product);
hər biri öz git worktree və branch-ında işləyib, `main`-ə inteqrasiya Agent 01 tərəfindən edilib.
Qaydalar: [`CLAUDE.md`](CLAUDE.md), rol təsvirləri: [`docs/agents/`](docs/agents/), arxitektura:
[`docs/architecture/overview.md`](docs/architecture/overview.md).
