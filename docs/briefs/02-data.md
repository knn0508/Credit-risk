# Brief 02 — Data
**Objective:** təkrarlana bilən data pipeline + audit. **Inputs:** data/raw/*.csv (mövcuddur), docs/contracts/data-contract.md.
**Scope:** src/data/, configs/data.yaml. **İşlər:** inventar+data dictionary → keyfiyyət auditi → 6 köməkçi cədvəlin SK_ID_CURR aqreqasiyası → processed parquet + schema.json.
**Interface:** data-contract çıxışları; adlandırma qaydası. **Acceptance:** train 307511 sətir/unikal SK_ID_CURR; join-dən sonra sətir sayı dəyişmir; test və train schema fərqi sənədləşib; leakage şübhələri siyahıda.
**Tests:** join təhlükəsizliyi, unikallıq, null/tip schema. **Handoff:** docs/agent-handoffs/02-to-03-data-dictionary.md; kontrakt uyğunsuzluğu varsa 01-ə sorğu.
