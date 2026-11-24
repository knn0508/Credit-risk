# Brief 06 — Product
**Objective:** API + Streamlit + Docker, əvvəl mock bundle ilə.
**Scope:** api/, app/, deployment/, integration/smoke testlər. **Interface:** contracts/prediction-api.md, model-bundle.md (yükləmə qaydası), explanation.md.
**Acceptance:** /health,/model-info,/predict,/explain,/predict/batch işləyir; approved olmayan bundle DEV rejimində xəbərdarlıqla; loglarda giriş dəyəri yoxdur; disclaimer var. **Tests:** schema, 422/503, batch, smoke. **Handoff:** işə salma təlimatı → 01 final qəbul.
