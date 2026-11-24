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

## Tam data təsdiqi (03, CPU; 04-ün run_cv protokolu: seed 42, 80% train hissəsi 246008 sətir, holdout toxunulmaz, 5-fold OOF)
Giriş: ədədi processed sütunlar + 23 ft_ (236 sütun), code_gender xaric; logreg = SimpleImputer(median)+StandardScaler+LogisticRegression(max_iter=300).
| Variant | ROC-AUC | PR-AUC | fold std AUC / PR |
|---|---|---|---|
| winsorize yoxdur | 0.7656 | 0.2470 | 0.0003 / 0.0035 |
| Winsorizer(bütün ədədi, 1/99) | 0.7673 | 0.2503 | 0.0008 / 0.0027 |
Qazanc +0.0017 AUC (fold std-dən böyük), +0.0033 PR (təxminən 1 std): kiçik, amma ardıcıl. Qərar: xətti modeldə winsorize istifadə et; ağac modellərdə yox. 04 təsdiqləməlidir.
