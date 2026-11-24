# Validation report — <MODEL_VERSION>  (ŞABLON)
Protokol: reports/evaluation-protocol.md. Holdout yalnız bu hesabatda, hədlər dondurulduqdan sonra.

1. **Xülasə:** nəticə (validated/rədd), əsas rəqəmlər, açıq risklər.
2. **Model müqayisəsi (OOF CV):** logreg / lgbm / xgb / catboost / rf — ROC-AUC, PR-AUC, fold std, vaxt.
3. **Kalibrasiya (OOF):** raw vs platt vs isotonic — Brier, ECE; reliability cədvəli/şəkil (reports/figures/).
4. **Hədd variantları (OOF):** cədvəl (low_max, medium_max → band payı, defolt dərəcəsi, lift, High precision/recall).
5. **Holdout:** ROC/PR-AUC + bootstrap CI, Brier, ECE, band cədvəli, confusion (High=müsbət), OOF ilə fərq (sabitlik).
6. **Cost sensitivity (FN:FP 2…10, FƏRZİYYƏ).**
7. **Subgroup audit:** run_audit çıxışı + şərh; yaş qrupları üzrə sistematik fərq.
8. **SHAP + müstəqil leakage baxışı:** qlobal top-15, şübhəli feature varmı.
9. **Məhdudiyyətlər və tövsiyə:** risk_policy təklifi (proposal), 01 təsdiqi gözlənilir.
