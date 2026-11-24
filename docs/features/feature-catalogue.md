# Feature catalogue — QARALAMA v0.1 (Agent 03)
Status: draft. Real EDA, null faizləri və leakage hesabatı 02-nin `data/processed` + `schema.json`-undan sonra.
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

## B. Aqreqat feature-lar (mənbə: 02-nin SK_ID_CURR səviyyəli aqreqatları; yalnız müraciətə qədər tarixçə)
Planlaşdırılan qruplar (dəqiq sütun adları 02 `schema.json`-dan sonra):
- bureau: aktiv/bağlı kredit sayı, cəmi borc / kredit limiti nisbəti (`ft_bureau_debt_credit_ratio`), max gecikmə (CREDIT_DAY_OVERDUE), bureau_balance-dan DPD statusu payı.
- previous_application: əvvəlki müraciət sayı, Refused payı (`ft_prev_refused_share`), orta amt_application/amt_credit fərqi.
- installments_payments: gecikmiş ödəniş payı, orta gecikmə günü (DAYS_ENTRY_PAYMENT − DAYS_INSTALMENT), ödəniş/taksit nisbəti.
- POS_CASH / credit_card: max SK_DPD, orta limit istifadəsi (`ft_cc_utilization`).
Yoxdursa (tarixçəsiz müştəri): say=0, nisbət=NaN + `*_has_history` flag.

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
