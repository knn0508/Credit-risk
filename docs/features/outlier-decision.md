# Outlier / winsorize qərarı (Agent 03; 04 ilə razılaşdırılmalıdır)
**Problem:** `amt_income_total` max/p99 ≈ 248 (max 1.17e8, p99 4.72e5). Outlier-lər silinmir (data-contract v1.0 qərar 9).
**Qərar:**
- Ağac modelləri (LightGBM/XGBoost/CatBoost — əsas model): heç nə etmə; split-lər monoton çevirməyə həssas deyil. `ApplicationFeatures`/`AggregateFeatures` winsorize etmir.
- Xətti modellər (logreg baseline): `src.features.Winsorizer` (1/99 faiz, sərhədlər YALNIZ fit-də train fold-da öyrənilir, NaN saxlanır) Pipeline-da imputer-dən əvvəl.
  `Winsorizer(columns=<bütün ədədi sütunlar>)` tövsiyə olunur; default (4 sütun: amt_income_total, ft_income_per_person, ft_credit_income_ratio, ft_annuity_income_ratio) təsiri çox kiçikdir.
**Ölçmə (logreg, SimpleImputer(median)+StandardScaler, 50k nümunə, 5-fold OOF, seed 42; tək işləmə, fold std yoxdur):**
| Variant | ROC-AUC | PR-AUC |
|---|---|---|
| winsorize yoxdur | 0.7609 | 0.2456 |
| Winsorizer() default (4 sütun) | 0.7610 | 0.2459 |
| Winsorizer(bütün ədədi) | 0.7632 | 0.2537 |
Kiçik qazanc (+0.002 AUC / +0.008 PR); tam data və fold std ilə 04 təsdiq etməlidir. Əsas modelə təsiri gözlənilmir.
**Paritet:** Winsorizer sərhədləri joblib ilə bundle-da saxlanır; inference eyni sərhədlə kəsir (tests/unit/test_feature_parity.py).
