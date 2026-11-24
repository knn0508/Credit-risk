# 0001 — Split, seed, hədd yanaşması, kitabxanalar (qaralama, Agent 01)
- Seed 42 hər yerdə (configs/training.yaml).
- Yalnız application_train-dən: stratified 80/20 (train / holdout), train daxilində 5-fold stratified CV.
  Holdout yalnız son qiymətləndirmə (05) üçündür; tuning/threshold holdout-da seçilmir — hədlər 05-in ayrıca
  validation hissəsində (CV out-of-fold və ya train-dən ayrılmış calibration seti) seçilir. 05 protokolu dəqiqləşdirir.
  application_test heç yerdə model/hədd seçimində istifadə olunmur (yalnız schema/inference smoke).
- Metrikalar: ROC-AUC, PR-AUC əsas; accuracy əsas deyil. Kalibrasiya: Brier + calibration curve.
- Risk bandı: kalibrasiya olunmuş p ≤ low_max → Low; ≤ medium_max → Medium; əks halda High.
  Hədlər configs/risk_policy.yaml-da; 05 təklif edir, 01 validation-a baxıb təsdiqləyir; biznes təsdiqi olmadan "fərziyyə".
- Kitabxanalar (təklif): pandas, pyarrow, scikit-learn, lightgbm, xgboost, catboost, shap, fastapi, pydantic, streamlit,
  pytest, joblib. Əlavə = 01-ə sorğu (requirements.txt).
- Bundle serializasiyası: joblib + JSON metadata (bax contracts/model-bundle.md).
