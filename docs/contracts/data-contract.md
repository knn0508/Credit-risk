# Data kontraktı — v1.0 DONDURULUB (02 auditi əsasında; dəyişiklik yalnız 01 təsdiqi ilə)
**Grain:** 1 sətir = 1 kredit müraciəti, açar `SK_ID_CURR` (unikal, null deyil).
**Target:** `TARGET` (0/1) yalnız application_train-də. application_test-də yoxdur; model/hədd seçimində istifadə olunmur.
**Cədvəllər:** application_{train,test} (grain-dir); bureau (SK_ID_BUREAU), bureau_balance (SK_ID_BUREAU+MONTHS_BALANCE),
previous_application (SK_ID_PREV), POS_CASH_balance, credit_card_balance, installments_payments (SK_ID_PREV, SK_ID_CURR)
— hamısı one-to-many: ƏVVƏL SK_ID_CURR-ə aqreqasiya, sonra left-join.
**Join qaydaları:** join-dən əvvəl/sonra sətir sayı bərabər; SK_ID_CURR unikal; testlər src/data-da (02).
bureau_balance → əvvəl SK_ID_BUREAU, sonra SK_ID_CURR.
**Leakage:** proqnoz anında məlum olmayan sahə feature deyil; TARGET və ondan törəyən heç nə. Aqreqatlar yalnız
müraciət anına qədər olan tarixçəni əks etdirir (Home Credit-də DAYS_* mənfi = keçmiş). Şübhəli sahələr 02/03 siyahıya salır.
**Çıxışlar (02→03/04):** `data/processed/application_train.parquet`, `application_test.parquet` (SK_ID_CURR + aqreqat sütunlar;
TARGET yalnız train), `data/processed/schema.json` (sütun, dtype, nullable, mənbə cədvəl, aqreqasiya adı), quality report.
**Adlandırma:** snake_case kiçik hərf; aqreqat: `<mənbə>_<sütun>_<stat>` (məs. `bureau_amt_credit_sum_debt_max`);
orijinal application sütunları adını saxlayır (kiçik hərfə çevrilərək). 03 yeni feature-lara `ft_` prefiksi verir.
**Dəyişiklik:** yalnız 01 təsdiqi ilə; 02 audit nəticəsinə görə düzəliş sorğusu göndərir.

## v1.0 — audit qərarları (docs/data/quality-report.md, Agent 02; 01 qəbul etdi)
1. Train 307 511 sətir (unikal SK_ID_CURR, defolt 8.073%), test 48 744; schema fərqi yalnız TARGET. Train/test eyni emal qaydalarından keçir.
2. Sentinellər → NaN: `DAYS_EMPLOYED=365243` (+ `days_employed_is_anomalous` bayrağı); `CODE_GENDER`/`ORGANIZATION_TYPE`='XNA'; previous_application `DAYS_FIRST_DRAWING/FIRST_DUE/LAST_DUE/TERMINATION`=365243.
3. bureau_balance: bureau-da olmayan SK_ID_BUREAU sətirləri atılır (3 120 184, hesabatda sayı qeyd olunur).
4. POS_CASH / credit_card / installments öz SK_ID_CURR sütunu ilə aqreqasiya olunur (previous_application-a join YOX).
5. Tarixçəsizlik: NaN + `<mənbə>_has_history` bayrağı; 0 ilə doldurulmur.
6. Leakage: previous_application `DAYS_LAST_DUE_1ST_VERSION/DAYS_LAST_DUE/DAYS_TERMINATION/DAYS_FIRST_DRAWING` aqreqatdan XARİCDİR (yalnız DAYS_DECISION, məbləğ, status sahələri). Açmaq üçün 03+01 təsdiqi lazımdır.
7. `code_gender` processed-də qalır, model feature_names-də olmur (decisions/0002).
8. Zaman sütunu yoxdur → zaman-əsaslı split mümkün deyil (04/05 məhdudiyyət kimi model card-da qeyd edir). Train/test paylanma sürüşməsi (|SMD|<0.5) 04/05-ə məlumdur.
9. Outlier-lər (AMT_INCOME_TOTAL və s.) silinmir; winsorize/log qərarı 03/04-ündür.
