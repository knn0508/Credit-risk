# Prediction API kontraktı — QARALAMA v0.1
Endpointlər: `GET /health`, `GET /model-info`, `POST /predict`, `POST /explain`, `POST /predict/batch`.
**Request /predict:** `{"applicant": {<feature_name>: value, ...}, "request_id": "optional"}` —
`applicant` data-contract-dakı processed feature sütunlarıdır (SK_ID_CURR istəyə bağlı). Çatışmayan sahə → null + warning;
naməlum sahə → ignore + warning; tip xətası → 422.
**Response /predict:**
```json
{"prediction_id":"uuid4","timestamp":"ISO-8601 UTC","model_version":"...",
 "prediction_probability":0.0,"risk_band":"Low|Medium|High",
 "calibrated":true,"warnings":["..."],
 "disclaimer":"Qərar dəstəyidir; avtomatik təsdiq/rədd deyil."}
```
`prediction_probability` kalibrasiya olunmuş ehtimaldır (calibrator yoxdursa calibrated=false + warning).
**/explain:** /predict cavabı + `explanation` (bax explanation.md). **/batch:** `{"applicants":[...]}` → `{"results":[...]}`, max 10 000 sətir.
**/model-info:** model_version, algorithm, created_at, metrics, risk_policy_version, validation_status, feature_count.
**/health:** `{"status":"ok","model_loaded":bool}`.
**Xətalar:** 422 validasiya, 503 bundle yoxdur/təsdiqsiz. **Loglama:** prediction_id, model_version, band, latency; giriş dəyərləri YOX.
