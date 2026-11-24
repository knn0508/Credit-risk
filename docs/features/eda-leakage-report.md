# EDA + leakage hesabatı (Agent 03, avtomatik: notebooks/eda/eda_leakage_report.py)

Data: application_train, 307511 sətir, 229 processed sütun + 24 ft_. Defolt payı: 8.0729%.
Univariate AUC yalnız siqnal göstəricisidir (modelin keyfiyyəti deyil); 0.5 = siqnalsız.

## 1. Ən güclü 15 feature (|AUC−0.5|)
| feature | AUC | null % |
|---|---|---|
| ft_ext_source_mean | 0.284 | 0.1% |
| ft_ext_source_min | 0.309 | 0.1% |
| ft_ext_source_prod | 0.330 | 0.1% |
| ext_source_2 | 0.344 | 0.2% |
| ext_source_3 | 0.351 | 19.8% |
| bureau_days_credit_mean | 0.590 | 14.3% |
| days_birth | 0.583 | 0.0% |
| ft_age_years | 0.417 | 0.0% |
| ext_source_1 | 0.418 | 56.4% |
| ft_bureau_debt_credit_ratio | 0.581 | 17.0% |
| ft_employed_years | 0.421 | 18.0% |
| days_employed | 0.579 | 18.0% |
| bureau_active_mean | 0.575 | 14.3% |
| bureau_days_credit_max | 0.571 | 14.3% |
| ft_credit_goods_ratio | 0.569 | 0.1% |

## 2. Missingness
- >50% null olan sütun: 66 (processed), 2 (ft_).
- ft_ null (top 5): ft_cc_payment_balance_ratio 81%, ft_cc_utilization 72%, ft_employed_age_ratio 18%, ft_employed_years 18%, ft_bureau_debt_credit_ratio 17%
- Null-un özü siqnaldır? `*_has_history` bayraqlarının AUC-si:
  - bureau_has_history: AUC 0.480, tarixçəsizlər 14.3%
  - previous_application_has_history: AUC 0.508, tarixçəsizlər 5.4%
  - pos_cash_balance_has_history: AUC 0.506, tarixçəsizlər 5.9%
  - credit_card_balance_has_history: AUC 0.511, tarixçəsizlər 71.7%
  - installments_payments_has_history: AUC 0.507, tarixçəsizlər 5.2%

## 3. Leakage yoxlamaları
- OK : TARGET feature matrisində yoxdur
- OK : code_gender ft_-də yoxdur / model matrisindən çıxarılır
- OK : Şübhəli yüksək siqnal (|AUC−0.5|>0.25): yoxdur
- OK : Keçmiş-tarix sütunlarında müsbət (gələcək) dəyər: yoxdur
- Məlumat: gələcək son tarix (days_credit_enddate_*) müsbət ola bilər (kreditin planlı bitməsi, müraciət anında məlumdur): ['bureau_days_credit_enddate_min', 'bureau_days_credit_enddate_max']
- ft_ top |corr(TARGET)|: ft_ext_source_mean 0.222, ft_ext_source_min 0.185, ft_ext_source_prod 0.140, ft_cc_utilization 0.135, ft_age_years 0.078
- Dublikat ft_ sütunu: yoxdur

## 4. Outlier (winsorize/log qərarı üçün; silinmir)
- amt_income_total: p50 1.47e+05, p99 4.72e+05, max 1.17e+08, max/p99 = 247.6
- amt_credit: p50 5.14e+05, p99 1.85e+06, max 4.05e+06, max/p99 = 2.2
- ft_credit_income_ratio: p50 3.27, p99 13, max 84.7, max/p99 = 6.5
- ft_credit_term: p50 20, p99 37.8, max 45.3, max/p99 = 1.2

## 5. Nəticə
Avtomatik yoxlamalarda leakage əlaməti tapılmadı (DİQQƏT sətri yoxdur). Məhdudiyyət: bu, evristik yoxlamadır; Home Credit-də mütləq tarix olmadığı üçün aqreqatların "müraciətdən sonra" sətir daxil etmədiyi data özündən sübut oluna bilməz, yalnız DAYS_* işarəsi və siqnal gücü ilə dolayı yoxlanır.
