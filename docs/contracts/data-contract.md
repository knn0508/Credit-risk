# Data kontraktı — QARALAMA v0.1 (status: draft; 02-nin auditindən sonra dondurulur)
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
