# 03 -> 04: ft_ feature interfeysi (v0.2)
**Branch:** agent/03-features (main-ə 01 integrate edəndən sonra `scripts/agents/sync.sh`).
## İnterfeys
```python
from src.features import ApplicationFeatures, AggregateFeatures, EXCLUDED_PROTECTED_FEATURES
X = pd.read_parquet("data/processed/application_train.parquet").set_index("sk_id_curr")
ft = pd.concat([ApplicationFeatures().fit(X).transform(X), AggregateFeatures().fit(X).transform(X)], axis=1)
```
- Sklearn uyğun (`fit(X, y=None)`, `transform(X)`, `get_feature_names_out()`), STATELESS: fit heç nə öyrənmir -> fold leakage yoxdur.
- Giriş: processed DataFrame (kiçik hərfli sütunlar, data-contract v1.0). TARGET oxunmur. Index saxlanır.
- Çıxış: yalnız ft_ sütunları, sabit sıra, float64 (üç int8 sayğac xaric). NaN buraxılır (impute 04-ündür; tree modellər NaN qəbul edir).
- Sütunlar: `ApplicationFeatures` (16): ft_credit_income_ratio, ft_annuity_income_ratio, ft_credit_term, ft_credit_goods_ratio, ft_age_years,
  ft_employed_years, ft_employed_age_ratio, ft_income_per_person, ft_ext_source_{mean,min,prod,missing_cnt},
  ft_doc_count, ft_bureau_req_total_year, ft_days_registration_years, ft_id_publish_years.
  `AggregateFeatures` (7): ft_bureau_debt_credit_ratio, ft_bureau_overdue_credit_ratio, ft_prev_credit_application_ratio,
  ft_new_credit_to_prev_credit_max, ft_cc_utilization, ft_cc_payment_balance_ratio, ft_inst_payment_ratio.
- Model matrisi = processed sütunlar (target, sk_id_curr, EXCLUDED_PROTECTED_FEATURES xaric) + ft_ sütunlar. Strin kateqoriyalar (16 sütun) kodlaşdırması 04-ündür.
## Qeydlər
- Aqreqat tarixçəsizlik NaN-dır (0 deyil); `*_has_history` bayraqları processed-də var.
- ft_cc_utilization ~72%, ft_cc_payment_balance_ratio ~81% null (kart tarixçəsi yox).
- Təsiri ölçəndə: baseline (yalnız processed) vs +ft_ eyni CV fold-larla müqayisə et; sadələşdirmə rəyini mənə qaytar.
Testlər: tests/unit/test_application_features.py, test_aggregate_features.py (hamısı keçir).
