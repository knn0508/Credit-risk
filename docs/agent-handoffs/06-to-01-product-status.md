# 06 → 01: product statusu
- Branch agent/06-product; 94 test keçir (pytest tests -q), mock bundle ilə.
- /explain: src/explainability.ShapExplainer; bundle-da `background.parquet` (feature_names sütunları, ≤1000 sətir, train-dən) lazımdır, yoxdursa 503. **Kontrakt sorğusu:** model-bundle.md-ə bu fayl əlavə olunsun, 04 yazsın. Model Pipeline(`pre`,`clf`) olmalıdır (real logreg bundle belədir).
- İzah xam modelin log-odds-udur (kalibrasiyadan əvvəl) — UI/README-də qeyd olunub.
- Real bundle-lar hələ unvalidated və risk_policy.json yoxdur → yalnız ALLOW_DEV, və risk_policy.json olmadan yüklənmir. approved yolu mock ilə test olunub (real bundle ilə yox).
- Docker: deployment/Dockerfile (pinned deployment/requirements.txt, non-root, HEALTHCHECK, libgomp1), compose healthcheck-lərlə. BUILD YOXLANMAYIB — 01 yoxlayır.
- deployment/README.md: təmiz mühit təlimatı.
