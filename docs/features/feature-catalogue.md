# Feature catalogue — v0.2 (Agent 03)
Status: kod yazılıb və main-dədir: 23 ft_ (ApplicationFeatures 16 + AggregateFeatures 7). Hesabat: docs/features/eda-leakage-report.md.
Sadələşdirmə (04, LightGBM 5-fold OOF): ft_employed_anom silindi (dublikat). ft_bureau_overdue_credit_ratio və ft_bureau_req_total_year SAXLANDI (silmək AUC-ni ≤0.0002 dəyişir, PR -0.0017-ə qədər azalır).
Cəmi təsir: 228 -> 251 feature, ROC-AUC 0.7808 -> ~0.785 (+0.004), PR-AUC +0.003.
Adlandırma: yeni feature-lar `ft_` prefiksi (data-contract). Orijinal/aqreqat sütunlar 02-dən gəlir (kiçik hərf).
Null siyasəti: tree modellər üçün NaN saxlanır; xətti model üçün imputer transformer daxilində, YALNIZ train fold-da fit.

## A. application-dan törəmə (mənbə: application_*, 02-dən asılılıq yoxdur)
| Feature | Tip | Məntiq | Null siyasəti / məhdudiyyət |
|---|---|---|---|
| ft_credit_income_ratio | float | amt_credit / amt_income_total | income<=0 → NaN |
| ft_annuity_income_ratio | float | amt_annuity / amt_income_total (ödəniş yükü) | income<=0 → NaN |
| ft_credit_term | float | amt_credit / amt_annuity (təxmini müddət, ay) | annuity<=0 → NaN |
| ft_credit_goods_ratio | float | amt_credit / amt_goods_price | goods<=0 → NaN |
| ft_age_years | float | -days_birth / 365.25 | — |
| ft_employed_years | float | -days_employed / 365.25 | days_employed==365243 → NaN (anomaliya) |
| ft_employed_age_ratio | float | ft_employed_years / ft_age_years | employed NaN → NaN |
| ft_income_per_person | float | amt_income_total / cnt_fam_members | members<=0 → NaN |
| ft_ext_source_mean | float | ext_source_1..3 orta (mövcud olanlardan) | hamısı NaN → NaN |
| ft_ext_source_min / _prod | float | min / hasil | eyni |
| ft_ext_source_missing_cnt | int8 | NaN olan ext_source sayı | — |
| ft_doc_count | int8 | sum(flag_document_2..21) | — |
| ft_bureau_req_total_year | float | amt_req_credit_bureau_* cəmi (hour..year) | hamısı NaN → NaN |
| ft_days_registration_years, ft_id_publish_years | float | -days_*/365.25 | — |

## B. Aqreqat feature-lar (AggregateFeatures; mənbə: 02-nin SK_ID_CURR aqreqatları; tarixçəsiz -> NaN)
| Feature | Məntiq | Null (train) |
|---|---|---|
| ft_bureau_debt_credit_ratio | bureau_amt_credit_sum_debt_sum / bureau_amt_credit_sum_sum | 17% |
| ft_bureau_overdue_credit_ratio | bureau_amt_credit_sum_overdue_sum / bureau_amt_credit_sum_sum | 15% |
| ft_prev_credit_application_ratio | previous_application_amt_credit_mean / amt_application_mean | 6% |
| ft_new_credit_to_prev_credit_max | amt_credit / previous_application_amt_credit_max | 5% |
| ft_cc_utilization | credit_card_balance_amt_balance_mean / amt_credit_limit_actual_mean | 72% |
| ft_cc_payment_balance_ratio | amt_payment_current_mean / amt_balance_mean | 81% |
| ft_inst_payment_ratio | installments_payments_amt_payment_sum / amt_instalment_sum | 5% |
Payların özü (refused_mean, is_late_mean, dpd_share_*) 02-nin aqreqatlarındadır, təkrar hesablanmır.

## C. Leakage / risk siyahısı (ilkin)
- TARGET və törəməsi — feature deyil.
- Aqreqatlarda yalnız keçmiş (DAYS_* ≤ 0, MONTHS_BALANCE ≤ 0) sətirlər; gələcək dəyər (müsbət DAYS) yoxlanacaq.
- Həssas/ədalət (qərar 0002, insan təsdiqi): `code_gender` model feature-ı DEYİL (yalnız 05 audit); `src.features.EXCLUDED_PROTECTED_FEATURES` = ["code_gender"] -> 04 bundle metadata.excluded_protected_features. `ft_age_years` qalır, 05 audit edir.
- Proksi ola biləcək sahələr (işarələnib, 05 auditə baxır): `ft_age_years`, `cnt_children`, `name_family_status`, `region_*`/`region_rating_client*`, `organization_type`, `occupation_type`, `name_education_type`.
- Müraciət sonrası məlumat ola biləcək sahələr (məs. previous_application-da cari müraciətə aid olmayan, tarixi sonrakı sətirlər) 02/03 birgə yoxlayır.

## D. Növbəti addımlar
1. 02 processed + schema.json → real EDA (notebooks/eda), null/outlier/target-by-bin.
2. `src/features/` sklearn transformer (BaseEstimator+TransformerMixin, stabil sütun sırası, fit train fold-da).
3. `configs/feature_display_names.yaml` — YAZILDI (01 təsdiqi ilə); aqreqat adları 02 schema.json-dan sonra əlavə olunacaq.
4. Testlər: fit/transform, null davranışı, sütun sırası, TARGET yoxluğu.
