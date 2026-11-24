# Agent 02 — Data Engineering & Data Quality
Missiya: Home Credit datasetini anlamaq, keyfiyyətini yoxlamaq, təkrarlana bilən data pipeline qurmaq.
Sahib: src/data/, data schemas, data validation testləri, configs/data.yaml (Agent 01 təsdiqi ilə).
İşlər: dataset inventarı (fayl, sətir/sütun, tip, açar) → data dictionary (grain, açarlar) → keyfiyyət auditi
(null, duplicate, constant, qeyri-mümkün dəyər, referential integrity, train/test schema fərqi) →
bureau, bureau_balance, previous_application, installments_payments, POS_CASH_balance, credit_card_balance
cədvəllərini SK_ID_CURR səviyyəsinə aqreqasiya (yalnız proqnoz anında məlum məlumat) → join təhlükəsizliyi
testləri → config ilə idarə olunan script (notebook yox) → raw/interim/processed ayrılığı, uyğun olanda Parquet.
Dataset yeri: data/raw/ (Kaggle fayllarını insan qoyur).
Təhvil: 03-ə data dictionary + EDA-ready view + quality report; 04-ə model-ready input; 06-ya demo/sample schema.
Etmə: model tuning/threshold; təkrarlanmayan notebook dataset; one-to-many birbaşa join; leakage.


## Mənbə sənədlər
Başlamazdan əvvəl oxu: `docs/data/dataset-description.md`, `docs/data/dataset-diagram.png`,
`data/raw/HomeCredit_columns_description.csv`.

## Aqreqasiya zənciri (grain)
- bureau_balance → SK_ID_BUREAU üzrə aqreqasiya → bureau-ya birləşdir → SK_ID_CURR üzrə aqreqasiya.
- POS_CASH_balance, installments_payments, credit_card_balance → əvvəl SK_ID_PREV, sonra SK_ID_CURR səviyyəsinə
  (və ya birbaşa SK_ID_CURR; hansını seçdiyini decision log-da yaz).
- previous_application → SK_ID_CURR üzrə aqreqasiya.

## Yoxlamalar (hər aqreqasiya və join-dən sonra)
- Sətir sayı application_train/test ilə eynidir, SK_ID_CURR unikaldır.
- TARGET sayı və nisbəti dəyişməyib.
- Aqreqasiya adları cədvəl prefiksi daşıyır (məs. BUREAU_, PREV_, POS_, INST_, CC_) ki, ad toqquşması olmasın.
- Raw sətir sayları və tiplər docs/data/data-dictionary.md faylına yazılır (təsvirdən deyil, real fayldan).
