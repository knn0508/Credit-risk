# Handoff 02 → 04: model-ready input
Mənbə: `data/processed/application_{train,test}.parquet` + `schema.json` (data-contract v1.0). Yenidən qurmaq: `python -m src.data.build` (~35 s, deterministik).

## Rollar (schema.json `role` və aşağıdakı qaydalar)
| Rol | Sütun | Qayda |
|---|---|---|
| açar / identifikator | `sk_id_curr` | FEATURE DEYİL. Split, OOF (`oof_predictions.parquet`) və join üçün. |
| target | `target` | yalnız train (0/1, müsbət nisbət 8.073%). Test-də yoxdur; model/hədd seçimində test istifadə olunmur. |
| fairness-only | `code_gender` | `excluded_protected_features` = ["code_gender"] (decisions/0002). Processed-də qalır, `feature_names`-də OLMAMALIDIR. |
| feature | 228 sütun | 120 application + 108 aqreqat (schema.json `role=="feature"` 229 sətirdir; `code_gender` çıxarılandan sonra 228) |

Sütun tipləri (sample-schema.json, 230 giriş sahəsi = target xaric hamısı, sk_id_curr daxil): float 109, integer 67 (sk_id_curr daxil), binary 38, categorical 16.
Kateqorial sütunlar (string, NaN mümkün): name_contract_type, code_gender, flag_own_car, flag_own_realty, name_type_suite, name_income_type,
name_education_type, name_family_status, name_housing_type, occupation_type, weekday_appr_process_start, organization_type,
fondkapremont_mode, housetype_mode, wallsmaterial_mode, emergencystate_mode. Encoding 03/04-ündür (fit yalnız train fold-da).

## NaN siyasəti
- Data qatında İMPUTASİYA YOXDUR: NaN = "məlumat yoxdur / sentinel / tarixçə yoxdur". 164 sütun nullable, 66-sı >50% null.
- Tarixçəsizlik: `bureau_has_history`, `previous_application_has_history`, `pos_cash_balance_has_history`, `credit_card_balance_has_history`,
  `installments_payments_has_history` (1/0); həmin mənbənin `*_count`/`*_nunique` sütunları 0, qalan aqreqatlar NaN (sum daxil).
- Sentinel: `days_employed` NaN + `days_employed_is_anomalous` (1 = 365243 idi); `code_gender`/`organization_type` 'XNA' → NaN.
- Ağac modelləri (LightGBM/XGBoost/CatBoost) NaN-ı birbaşa qəbul edir; linear baseline üçün imputasiya + indikator preprocessor-da (train fold) olmalıdır.
- Outlier-lər silinməyib (məs. amt_income_total max 117M); winsorize/log 03/04 qərarıdır.

## Data versiyası
`schema.json` `meta.data_version` (16 hex) = raw faylların sha256-dan törənmiş kombinə id; `meta.raw_files` hər fayl üçün ölçü+sha256; `meta.git_commit` build kodu.
Bundle `metadata.data_version` bu dəyərdən götürülür (kontrakt: "fayl hash"); `meta.data_sha256` tam hash-dir. Cari: `3f3e26a7c9e1fee9`.
Raw data və ya build kodu dəyişərsə rebuild → `data_version` dəyişir; köhnə modelləri yenidən qiymətləndirmək lazımdır.

## Məhdudiyyətlər
- Zaman sütunu yoxdur → zaman-əsaslı split mümkün deyil (model card-da qeyd olunsun). Stratified/group CV `sk_id_curr` üzrə.
- Train/test paylanma sürüşməsi: `docs/data/quality-report.md` §2 (|SMD|<0.5).
- previous_application `DAYS_LAST_DUE*/TERMINATION/FIRST_DRAWING` leakage səbəbilə yoxdur (açmaq 03+01 təsdiqi).
