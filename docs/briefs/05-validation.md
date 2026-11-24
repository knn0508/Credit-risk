# Brief 05 — Validation
**Objective:** 04-dən müstəqil qiymətləndirmə, calibration, band hədləri, SHAP, fairness, model card.
**Scope:** src/evaluation/, src/explainability/, reports/. **Interface:** risk_bands.py band(p) funksiyası; calibrator.joblib; explanation.md formatı; configs/risk_policy.yaml təklifi (status: proposal).
**Acceptance:** ROC/PR-AUC, confusion matrix, Brier+calibration curve, cost matrix (fərziyyə etiketli), subgroup audit, model card. **Tests:** metrik funksiyaları, band sərhədləri, SHAP shape. **Handoff:** hesabat+hədd təklifi → 01, 04, 06.
