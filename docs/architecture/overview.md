# Arxitektura və scope (qaralama v0.1, sahib: Agent 01)

## Scope
Home Credit Default Risk üzərində defolt ehtimalı + risk bandı + izah verən qərar DƏSTƏYİ prototipi.
Avtomatik təsdiq/rədd YOXDUR. Hər cavabda disclaimer. Biznes hədləri təsdiqlənənədək fərziyyədir.
Scope-dan kənar: real vaxt data axını, avtomatik qərar, kauzal iddialar, fairness "həll"i (yalnız audit).

## Data axını
raw CSV (data/raw) → [02] interim (cədvəl başına SK_ID_CURR aqreqatları) → processed (1 sətir = 1 müraciət)
→ [03] feature pipeline (src/features, train/inference üçün EYNİ kod) → [04] training (fit yalnız train fold)
→ model bundle (artifacts/) → [05] müstəqil validation + calibrator + risk_policy + SHAP
→ [01] təsdiq → [06] API + Streamlit (bundle yükləyir, feature/band məntiqini təkrarlamır).

## Repo xəritəsi
src/data (02) · src/features (03) · src/models (04) · src/evaluation, src/explainability (05) ·
api, app, deployment (06) · configs (01; data.yaml→02, training.yaml→04, risk_policy.yaml→05 təklif)
docs/contracts (01) · docs/briefs (01) · docs/decisions (01) · reports (05) · artifacts/ və data/ Git-ə girmir.

## Qapılar (gate)
G1 data audit + data dictionary (02) → G2 feature spec + leakage yoxlaması (03, 02 ilə) →
G3 baseline + benchmark, eyni protokol (04) → G4 validation + calibration + hədd təklifi (05) →
G5 01 təsdiqi (risk_policy.status: approved, bundle təsdiqi) → G6 API/UI real bundle ilə (06) →
G7 təmiz mühitdə end-to-end qəbul (01).

## Ortaq prinsiplər
- Split: yalnız application_train; stratified hold-out (validation/holdout) + CV; test setə baxılmır. Bax decisions/0001.
- Reproducibility: seed=42, config, git SHA, data versiyası (fayl hash) bundle metadata-sında.
- Sensitiv data loglanmır; prediction_id korrelyasiya üçün istifadə olunur.
