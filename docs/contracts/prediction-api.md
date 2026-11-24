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
 "disclaimer":"Qərar dəstəyidir; avtomatik təsdiq/rədd deyil. Yalnız demo/prototip; real kredit qərarları üçün deyil."}
```
`prediction_probability` kalibrasiya olunmuş ehtimaldır (calibrator yoxdursa calibrated=false + warning).
**/explain:** /predict cavabı + `explanation` (bax explanation.md). **/batch:** `{"applicants":[...]}` → `{"results":[...]}`, max 10 000 sətir.
**/model-info:** model_version, algorithm, created_at, metrics, risk_policy_version, validation_status, feature_count.
**/health:** `{"status":"ok","model_loaded":bool}`.
**Xətalar:** 422 validasiya, 503 bundle yoxdur/təsdiqsiz. **Loglama:** prediction_id, model_version, band, latency; giriş dəyərləri YOX.

## Dəqiqləşdirmə v0.2
**/predict/batch:** `{"applicants":[...]}` → `{"results":[{"index":0,"status":"ok","prediction":{<predict cavabı>}} | {"index":1,"status":"error","error":{"code":"VALIDATION","message":"..."}}],"summary":{"total":n,"ok":k,"failed":m}}`.
Tək sətir xətası bütün batch-i yıxmır (HTTP 200); bütün sorğu səviyyəli xəta (>10 000 sətir, bundle yox) 422/503. Hər uğurlu sətirin öz prediction_id-si var; batch-in ayrıca `batch_id` (uuid4) sahəsi olur.
**/explain:** query param `include_values` (default `false`) — feature `value` yalnız true olanda qaytarılır; `top_n` default 5, max 10.
Hər iki halda giriş dəyərləri loga yazılmır.
**/model-info (v0.3):** cavaba `feature_names` (sıralı siyahı, bundle-dan) və `excluded_protected_features` əlavə olunur; UI formu bunlardan qurulur.
**/model-info (v0.3.1):** cavaba `warnings: [..]` əlavə olunur (məs. metadata-da `excluded_protected_features` açarı yoxdursa). Bundle yükləmə: approved bundle-da bu açar yoxdursa 503; DEV rejimində yalnız warning.
