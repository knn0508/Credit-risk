# Model bundle kontraktı — QARALAMA v0.1
Qovluq: `artifacts/models/<model_version>/` (Git-ə girmir). `model_version` = `<alg>-<YYYYMMDD>-<gitsha7>`.
Fayllar:
- `model.joblib` — `predict_proba(X)[:,1]` verən estimator (preprocessor daxil Pipeline ola bilər)
- `preprocessor.joblib` — fit train fold-da; train və inference EYNİ src/features kodundan istifadə edir
- `calibrator.joblib` — 05 verir; `predict(p_raw)->p_cal`; 04 mərhələsində `null` ola bilər (raw p istifadə olunur, warning)
- `feature_names.json` — sıralı siyahı; API giriş sırasını bununla yoxlayır
- `metadata.json`:
  `{model_version, algorithm, created_at, git_sha, seed, config_path, data_version(fayl hash), train_rows, positive_rate,
    feature_count, metrics:{roc_auc, pr_auc, brier?}, calibrated:bool, validation_status: "unvalidated|validated|approved",
    approved_by, risk_policy_version, library_versions}`
- `risk_policy.json` — configs/risk_policy.yaml-ın təsdiqlənmiş surəti (version, low_max, medium_max)
**Yükləmə qaydası (06):** metadata.validation_status=="approved" olmayan bundle yalnız `MOCK/DEV` rejimində; feature_names uyğunsuzluğu = xəta.
**Band:** `band(p_cal)`: p≤low_max Low; p≤medium_max Medium; əks halda High — bir funksiya, src/evaluation/risk_bands.py (05), 06 import edir.
**Status axını:** 04 → unvalidated; 05 → validated (+calibrator); 01 → approved.
**Əlavə (decisions/0002):** metadata.json-a `excluded_protected_features: [..]` əlavə olunur (məs. ["code_gender"]).
**Əlavə (05 protokolu, qəbul):** 04 bundle ilə yanaşı `artifacts/models/<model_version>/oof_predictions.parquet`
(SK_ID_CURR, fold, p_raw, TARGET) və `split.json` (train/holdout SK_ID_CURR siyahıları, seed) verir. Kalibrasiya və hədd seçimi
yalnız OOF-da; holdout yalnız son hesabat üçün. (decisions/0001 ilə uyğundur.)
