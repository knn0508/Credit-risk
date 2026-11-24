# Brief 04 — Modeling
**Objective:** eyni protokolla baseline+benchmark, bundle. **Inputs:** model-ready data (02+03), configs/training.yaml, decisions/0001.
**Scope:** src/models/. Sıra: Dummy → LogReg → RF/LightGBM/XGBoost/CatBoost; imbalance əvvəl resampling-siz. Test setə baxma.
**Interface:** contracts/model-bundle.md (validation_status=unvalidated, calibrator=None). **Acceptance:** 5-fold CV ROC-AUC/PR-AUC cədvəli, seed/config/data hash metadata-da, bundle yüklənib predict_proba işləyir.
**Tests:** bundle round-trip, feature order, təkrar run eyni nəticə. **Handoff:** bundle+reproducibility → 05.
