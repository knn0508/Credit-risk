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
