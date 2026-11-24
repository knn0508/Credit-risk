# Handoff 02 → 03: data dictionary + EDA-ready data
**Hazırdır** (branch `agent/02-data`; main-ə inteqrasiyadan əvvəl 03 öz worktree-sindən `data/processed/` ortaq symlink ilə oxuya bilər).
- Data: `data/processed/application_train.parquet` (307,511 × 231), `application_test.parquet` (48,744 × 230), `schema.json`
- Sənəd: `docs/data/data-dictionary.md` (sütun, dtype, null %, mənbə, stat), `docs/data/quality-report.md` (anomaliyalar, leakage şübhələri)
- Yenidən qurmaq: `python -m src.data.build` (~15 s, deterministik), sonra `python -m src.data.dictionary`.

## Qaydalar (data-contract v1.0)
- Sütunlar kiçik hərf; aqreqat adı `<mənbə>_<sütun>_<stat>`. `sk_id_curr` açar, `target` yalnız train.
- Sentinel/XNA → NaN; `days_employed_is_anomalous` bayrağı (55,374 sətir).
- Tarixçəsizlik: `<mənbə>_has_history` ∈ {0,1}; `*_count`/`*_nunique` = 0; qalan aqreqatlar NaN (0 ilə doldurulmayıb; "heç nə müşahidə olunmayıb" NaN-dır, sum daxil).
- bureau_balance əvvəl SK_ID_BUREAU, sonra SK_ID_CURR; bureau-da olmayan 3,120,184 sətir atılıb.
- previous_application `DAYS_LAST_DUE*/TERMINATION/FIRST_DRAWING` aqreqata daxil deyil (leakage, açmaq 03+01 təsdiqi).
- `code_gender` var (qərar 0002: model feature-ı deyil). Outlier-lər silinməyib.
- Train/test paylanma sürüşməsi: `docs/data/quality-report.md` §2.

## Məlum məhdudiyyətlər
- Zaman sütunu yoxdur → zaman split mümkün deyil.
- Aqreqatlar sadə statistikadır (count/sum/mean/min/max); nisbət, trend, son-N-ay pəncərələri 03-ün `ft_` işidir.
