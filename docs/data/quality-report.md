# Data Quality Report (Agent 02)
Mənbə: `python -m src.data.inventory` və `python -m src.data.audit` (real fayllar, data/raw). Xam nəticələr: `data/interim/inventory.json`, `data/interim/audit.json`.

## 1. Inventar
| Cədvəl | Sətir | Sütun | Grain / açar |
|---|---|---|---|
| application_train | 307,511 | 122 | SK_ID_CURR unikal |
| application_test | 48,744 | 121 | SK_ID_CURR unikal; train ilə kəsişmə 0 |
| bureau | 1,716,428 | 17 | SK_ID_BUREAU unikal; SK_ID_CURR-ə many-to-one |
| bureau_balance | 27,299,925 | 3 | (SK_ID_BUREAU, MONTHS_BALANCE) təkrarsız |
| previous_application | 1,670,214 | 37 | SK_ID_PREV unikal |
| POS_CASH_balance | 10,001,358 | 8 | aylıq, SK_ID_PREV + SK_ID_CURR |
| credit_card_balance | 3,840,312 | 23 | aylıq, SK_ID_PREV + SK_ID_CURR |
| installments_payments | 13,605,401 | 8 | ödəniş/taksit, SK_ID_PREV + SK_ID_CURR |

Pozulmuş (ragged) CSV sətri yoxdur. Train: TARGET ∈ {0,1}, null yoxdur, defolt nisbəti 8.073% (qeyri-balanslı).

## 2. Train/test schema
- Yeganə fərq: `TARGET` (yalnız train). Tip uyğunsuzluğu yoxdur, konstant sütun yoxdur, tam təkrar sətir yoxdur.
- Paylanma sürüşməsi (standartlaşdırılmış orta fərqi, ən böyük): flag_email −0.46, amt_req_credit_bureau_qrt −0.35, amt_req_credit_bureau_mon +0.28,
  amt_goods_price +0.21, amt_credit +0.20. Heç biri >0.5 deyil, lakin 04/05 sürüşməni bilməlidir. Test seçimdə istifadə olunmur; yalnız təsviridir.

## 3. Anomaliyalar və emal qərarları
| Məsələ | Say | Qərar (processed data) |
|---|---|---|
| `DAYS_EMPLOYED = 365243` (sentinel) | 55,374 (= ORGANIZATION_TYPE 'XNA' sayı) | NaN-a çevrilir + `days_employed_is_anomalous` bayrağı |
| `CODE_GENDER = 'XNA'` | 4 | NaN (kateqoriya itirilmir, imputasiya 04/03) |
| `ORGANIZATION_TYPE = 'XNA'` | 55,374 | NaN; sentinel DAYS_EMPLOYED ilə eyni sətirlər |
| previous_application `DAYS_FIRST_DRAWING/FIRST_DUE/LAST_DUE/TERMINATION` = 365243 | 934,444 / 40,645 / 211,221 / 225,913 | NaN-a çevrilir (aqreqatdan əvvəl) |
| previous_application `DAYS_LAST_DUE_1ST_VERSION` > 0 (sentinel deyil) | 224,392 | Planlaşdırılmış gələcək tarix; aqreqatda istifadə OLUNMUR (leakage şübhəsi, bax §5) |
| bureau `DAYS_CREDIT_ENDDATE` > 0 | 602,603 | Normal (müraciət anında məlum planlı bitmə); saxlanır |
| installments `AMT_PAYMENT` null/0 | 4,345 | Aqreqatda NaN kimi qalır; fərq hesabı null-safe |
| credit_card `AMT_DRAWINGS_CURRENT` < 0 | 3 | Əhəmiyyətsiz; clip(0) |
| `AMT_INCOME_TOTAL` max 117,000,000 | 1 sətir sinfi | Real outlier; silinmir, 03/04 winsorize/log qərar verir |
| `OBS_30_CNT_SOCIAL_CIRCLE` max 348, `CNT_CHILDREN` max 19 | az | Outlier; silinmir |
| Yaş aralığı | 20.5–69.1 il | Normal; `DAYS_BIRTH` mənfi (keçmiş) |
| EXT_SOURCE_1/2/3 | 0–1 aralığında | Normal |

Bütün `DAYS_*` (application, bureau, previous, installments) və `MONTHS_BALANCE` sentinel xaricində ≤ 0-dır: tarixçə müraciət anına nisbətən keçmişdədir.

## 4. Referential integrity
- bureau, previous_application, POS_CASH, credit_card, installments: SK_ID_CURR null deyil və hamısı application (train ∪ test) içindədir (orphan = 0).
- Hər SK_ID_PREV bir SK_ID_CURR-ə aiddir (çoxlu-sahib 0). POS/CC/installments-dakı SK_ID_CURR previous_application ilə uyğun gəlir (uyğunsuzluq 0).
- **Problem 1:** bureau_balance-da **3,120,184 sətir** (11.4%) SK_ID_BUREAU-su bureau-da yoxdur → SK_ID_CURR-ə bağlanmır. Qərar: aqreqasiyadan çıxarılır, sayı hesabata yazılır.
- **Problem 2:** POS/CC/installments-da SK_ID_PREV-in previous_application-da olmaması: 37,422 / 11,372 / 38,847 fərqli SK_ID_PREV. Qərar: bu cədvəllər öz SK_ID_CURR sütunu ilə aqreqasiya olunur (previous_application-a join EDİLMİR).
- Əhatə: müştərilərin bir hissəsində tarixçə yoxdur (bureau train-in 263,491 müraciətində; credit_card yalnız 86,905). Tarixçəsizlik → NaN + `<mənbə>_has_history` bayrağı (0 ilə doldurulmur).

## 5. Leakage şübhələri
1. `previous_application.DAYS_LAST_DUE_1ST_VERSION`, `DAYS_LAST_DUE`, `DAYS_TERMINATION`, `DAYS_FIRST_DRAWING`: əvvəlki kreditin sonrakı həyat dövrünü əks etdirir; müraciətə nisbətən tarixlər mənfi olsa da, onların dəyərləri əvvəlki kreditin sonradan nə baş verdiyini göstərə bilər. Əvvəlki kreditlər müraciətdən əvvəl bağlanıbsa məlumdur, qeyri-müəyyəndirsə risklidir. İlkin qərar: yalnız `DAYS_DECISION`, məbləğ və status sahələri aqreqatlanır; qalanlar 03/01 ilə razılaşdırılana qədər xaric.
2. `bureau.DAYS_ENDDATE_FACT` / `DAYS_CREDIT_UPDATE`: hesabat tarixinə görə yenilənir; mənfi olduğu üçün keçmişdir, lakin snapshot vaxtı bilinmir. Qeyd olunur.
3. Dataset snapshot-dır: bütün tarixçə sahələri müraciətə nisbətəndir, amma TARGET müraciətdən sonrakı performansdan törənir. Ayrıca zaman sütunu olmadığı üçün zaman-əsaslı split mümkün deyil (04/05 üçün məhdudiyyət).
4. TARGET və ondan törəyən heç bir sütun processed feature-lara daxil edilmir.
5. `code_gender` processed data-da QALIR (qərar 0002: model feature-ı deyil, yalnız 05 fairness auditi üçün).

## 6. Null səviyyələri (yüksək)
previous_application `RATE_INTEREST_PRIMARY/PRIVILEGED` 99.6%; `AMT_DOWN_PAYMENT` 53.6%; bureau `AMT_ANNUITY` 71.5%, `AMT_CREDIT_MAX_OVERDUE` 65.5%;
application bina məlumatı (`COMMONAREA_*` və s.) ~70%; `AMT_REQ_CREDIT_BUREAU_*` 13.5%. Null çox vaxt "məlumat yoxdur" mənasındadır, informativdir: 03 ayrıca bayraq düşünə bilər.
