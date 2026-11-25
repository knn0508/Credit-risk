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
**Törəmə feature-lar (v0.4):** `applicant` ft_* sahələrini göndərməyə bilər. API onları train ilə EYNİ `src/features` kodundan (stateless) xam sahələrdən hesablayır; sorğuda verilmiş ft_* üstünlük təşkil edir. Xam giriş çatışarsa nəticə NaN (train davranışı). Cavabda warning: "N törəmə (ft_) feature avtomatik hesablandı".

## Demo bank endpoint v0.5 — `POST /bank/credit-check`
Yalnız demo (bank-website). Müştəri DB-dədir (`bank-website/db/bank.db`, env `BANK_DB`); sorğu yalnız PIN daşıyır.
**Request:** `{"pin": "AFPK054"}` — 7 simvol, `[A-Z0-9]`, ən azı 1 hərf və 1 rəqəm. Kiçik hərf qəbul edilir (böyüdülür).
**Response 200:** `{"customer":{"first_name","last_name","amt_income_total","amt_credit","amt_annuity","name_contract_type"},
"prediction_id","model_version","prediction_probability","risk_band":"Low|Medium|High","explanation":{<explanation.md, top_n=3, dəyərsiz>}|null,"warnings":[..],"disclaimer":".."}`.
Xam feature sətri brauzerə QAYTARILMIR. Skor və izah `/explain` ilə eyni koddan gəlir.
**Xətalar:** 422 PIN formatı yanlış · 404 PIN tapılmadı (ümumi mesaj) · 503 bundle yoxdur/təsdiqsiz.
**Loglama:** PIN və müştəri dəyərləri loga yazılmır (yalnız prediction_id, model_version, band, latency).
**CORS:** `CORS_ORIGINS` env (default `http://localhost:5173`). Nəticə qərar dəstəyidir, təsdiq/rədd deyil.

### `POST /bank/apply` (v0.5.1) — yeni müraciətçi
PIN DB-də yoxdursa (`/bank/credit-check` → 404) UI müraciət formasını göstərir. **Sıra: ƏVVƏL DB-yə yazılır (commit), SONRA skor sorğusu.**
**Request:** `pin, first_name, last_name, birth_date (YYYY-MM-DD, yaş 18–80), name_contract_type, amt_credit, term_months (6–360), amt_income_total, name_income_type, employed_years, name_education_type, name_family_status, name_housing_type, cnt_children, flag_own_car (Y|N), flag_own_realty (Y|N), amt_goods_price?` — kateqoriyalar dataset dəyərləridir (Literal).
**Yazılan sütunlar:** formdan gələnlər + `sk_id_curr` (max+1), `days_birth`, `days_employed`, `cnt_fam_members` (təxmini), `amt_annuity` (= amt_credit / term_months, faizsiz təxmin). Qalan feature-lar NULL (bureau/ext_source yoxdur → skor daha az dəqiqdir).
**Response 200:** `/bank/credit-check` ilə eyni. **Xətalar:** 409 PIN artıq var · 422 yanlış dəyər/PIN · 503 bundle yoxdur (bu halda heç nə yazılmır). Skor uğursuz olarsa qeyd DB-də qalır.

### v0.5.2 — NULL feature-lar izahda göstərilmir
`/bank/credit-check` və `/bank/apply` cavabında `explanation` yalnız modelə **real (NULL olmayan)** dəyər gedən feature-lardan qurulur (top_n=10 hesablanır, NULL olanlar atılır, 3-ə kəsilir). Bütün giriş NULL olanda sayıma çevrilən `ft_doc_count`, `ft_ext_source_missing_cnt`, `ft_bureau_req_total_year` də "məlum deyil" sayılır. Skor/band/ehtimal DƏYİŞMİR (yalnız izah süzülür). Cavaba `data_coverage` (0–1: NULL olmayan model feature payı) əlavə olunub; UI `< 0.5` olanda "ilkin qiymətləndirmə" qeydi göstərir.
`/bank/apply` request-ə əlavə: `region_rating_client` (1|2|3), `has_work_phone`, `has_mobile_phone`, `has_email` (bool) → `region_rating_client(_w_city)`, `flag_work_phone`, `flag_mobil`+`flag_cont_mobile`, `flag_email`.

## Deploy env (v0.6, Cloudflare Pages + Worker proxy + HF Space + Supabase + R2)
| Env | Harada | Məna |
|-----|--------|------|
| `DATABASE_URL` | HF Space secret | Supabase Postgres (pooler). Təyin olunubsa `api/bank.py` Postgres, yoxsa SQLite (`BANK_DB`) |
| `BUNDLE_DIR`, `ALLOW_DEV` | HF Space | bundle yolu (`/models/current`), təsdiqsiz bundle üçün `1` |
| `CORS_ORIGINS` | HF Space var | Pages origin-i |
| `R2_ACCOUNT_ID/_ACCESS_KEY_ID/_SECRET_ACCESS_KEY/_BUCKET`, `MODEL_VERSION` | HF Space secret | start-da `deployment/hf-space/fetch_bundle.py` bundle-ı `models/<ver>/` altından çəkir |
| `ORIGIN_URL`, `ALLOWED_ORIGIN` | Worker vars | Space URL-i, Pages origin-i |
| `VITE_API_URL` | Pages build var | Worker URL-i (frontend `/bank/*` çağırışlarına prefiks) |
Endpoint kontraktı dəyişmir. Sorğu yolu: Pages → Worker (CORS, rate limit) → Space (FastAPI).
