# Train vs Test drift (Agent 02, `python -m src.data.drift`)
Data versiyası: `3f3e26a7c9e1fee9` · train 307,511 / test 48,744 · 229 sütun.
Yalnız təsviri: test target-sizdir və model/hədd seçimində istifadə olunmur. PSI: <0.1 sabit, 0.1–0.25 orta, ≥0.25 böyük. Numerik PSI train desil bin-ləri ilə (NaN ayrıca bin), kateqorial PSI kateqoriya payları ilə (train-də olmayan kateqoriya ayrıca bin).

## Xülasə
- PSI ≥ 0.25 (böyük): **13** sütun
- 0.1 ≤ PSI < 0.25 (orta): **2** sütun
- PSI < 0.1 (sabit): **214** sütun
- Maksimum PSI: 1.72458 (`bureau_months_count_max`)
- Orta PSI: 0.09437

## Ən çox sürüşən 25 sütun
| sütun | növ | PSI | SMD | null% train | null% test |
|---|---|---|---|---|---|
| bureau_months_count_max | numeric | 1.72458 | -0.5435 | 70.01 | 13.2 |
| bureau_months_count_sum | numeric | 1.62508 | -0.4059 | 70.01 | 13.2 |
| bureau_dpd_share_mean | numeric | 1.58192 | 0.1147 | 70.01 | 13.2 |
| bureau_dpd_months_sum | numeric | 1.57392 | 0.0251 | 70.01 | 13.2 |
| bureau_dpd_months_max | numeric | 1.56623 | -0.0533 | 70.01 | 13.2 |
| bureau_months_oldest_max | numeric | 1.56501 | -0.0516 | 70.01 | 13.2 |
| bureau_dpd_share_max | numeric | 1.56493 | 0.055 | 70.01 | 13.2 |
| bureau_dpd_severe_months_sum | numeric | 1.55503 | 0.0437 | 70.01 | 13.2 |
| bureau_has_bb_sum | numeric | 1.34085 | -1.0405 | 14.31 | 13.18 |
| bureau_amt_annuity_sum | numeric | 1.22985 | 0.0048 | 73.98 | 21.6 |
| bureau_amt_annuity_mean | numeric | 1.22801 | 0.0081 | 73.98 | 21.6 |
| amt_req_credit_bureau_mon | numeric | 0.42954 | 0.2818 | 13.5 | 12.41 |
| amt_req_credit_bureau_qrt | numeric | 0.28 | -0.3544 | 13.5 | 12.41 |
| name_contract_type | categorical/binary | 0.21114 |  | 0.0 | 0.0 |
| flag_email | categorical/binary | 0.1242 | -0.4579 | 0.0 | 0.0 |
| ext_source_1 | numeric | 0.0846 | 0.0045 | 56.38 | 42.12 |
| amt_goods_price | numeric | 0.08118 | 0.2051 | 0.09 | 0.0 |
| amt_credit | numeric | 0.07983 | 0.2044 | 0.0 | 0.0 |
| credit_card_balance_months_balance_min | numeric | 0.07775 | -0.0092 | 71.74 | 65.84 |
| pos_cash_balance_months_balance_min | numeric | 0.07439 | 0.0407 | 5.88 | 1.92 |
| days_id_publish | numeric | 0.06695 | 0.0381 | 0.0 | 0.0 |
| previous_application_canceled_sum | numeric | 0.06599 | -0.1782 | 5.35 | 1.94 |
| previous_application_days_decision_min | numeric | 0.06494 | 0.0235 | 5.35 | 1.94 |
| amt_req_credit_bureau_week | numeric | 0.0631 | 0.1543 | 13.5 | 12.41 |
| previous_application_days_decision_max | numeric | 0.05732 | 0.0088 | 5.35 | 1.94 |

## Null nisbəti 5 faiz bəndindən çox fərqlənən sütunlar
`bureau_months_count_max`, `bureau_months_count_sum`, `bureau_dpd_share_mean`, `bureau_dpd_months_sum`, `bureau_dpd_months_max`, `bureau_months_oldest_max`, `bureau_dpd_share_max`, `bureau_dpd_severe_months_sum`, `bureau_amt_annuity_sum`, `bureau_amt_annuity_mean`, `ext_source_1`, `credit_card_balance_months_balance_min`, `credit_card_balance_amt_drawings_current_mean`, `credit_card_balance_amt_receivable_principal_mean`, `credit_card_balance_amt_balance_mean`, `credit_card_balance_amt_receivable_principal_max`, `credit_card_balance_amt_balance_max`, `credit_card_balance_amt_drawings_current_sum`, `credit_card_balance_sk_dpd_def_max`, `credit_card_balance_amt_credit_limit_actual_mean`, `credit_card_balance_sk_dpd_mean`, `credit_card_balance_sk_dpd_max`, `credit_card_balance_amt_credit_limit_actual_max`, `credit_card_balance_sk_dpd_def_mean`

## Əsas tapıntı: bureau_balance əhatəsi train və test-də fərqlidir
Bureau tarixçəsi olan müraciətlər arasında bureau_balance qeydi olanların payı: **train 35.0%**, **test 100.0%**. Xam fayllardan müstəqil yoxlanıb (bu build xətası deyil, datasetin xüsusiyyətidir). Nəticə: `bureau_months_*`, `bureau_dpd_*`, `bureau_has_bb_sum` aqreqatları train-də bureau müştərilərinin ~65%-i üçün NaN, test-də demək olar heç biri üçün NaN deyil. Bu sütunların PSI-si yüksək olmasının əsas səbəbi budur (dəyərlərin yox, itkinin sürüşməsi).
**Tövsiyə:** 04/05 bu sütunları feature-a daxil edəndə (a) itkin pattern-in train-də target ilə əlaqəsini yoxlasın, (b) bu sütunlarsız baseline ilə müqayisə etsin, (c) validation nəticələrini test paylanmasına ötürməsin; model train itkisini 'bureau_balance yoxdur' siqnalı kimi öyrənə bilər ki, test-də mövcud deyil. Qərar 04/05/01-indir; data qatında silinmir.

## Şərh (05/04 üçün)
- Test-in null pattern-i train ilə müqayisə olunur: böyük null fərqi imputasiya/indikator qərarlarına təsir edə bilər.
- Sürüşmə yüksək olan sütunlar üçün model performansının sabitliyi 05-in validation-ında ayrıca yoxlanmalıdır (test labelsizdir, ona görə yalnız paylanma müqayisəsidir).
- Bu sürüşmə həm də məlum Kaggle split xüsusiyyətidir; real istehsal drift monitorinqi üçün eyni PSI funksiyaları `src/data/drift.py`-dən istifadə oluna bilər.
