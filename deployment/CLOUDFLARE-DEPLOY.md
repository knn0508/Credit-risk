# Deploy runbook: Pages + Worker + HF Space + Supabase + R2 (Streamlit DAXİL DEYİL)
```
Browser → Pages (frontend) → Worker (CORS, rate limit) → HF Space (FastAPI) → Supabase (customers) + R2 (model bundle)
```
HF Space boş qalanda yatır: ilk sorğu 30–60 s. Supabase free layihə 7 gün aktivsizlikdə pauza olunur.

## 1. Supabase
New project → Settings → Database → Connection string (Session pooler URI) → `DATABASE_URL`.
    pip install "psycopg[binary]"
    DATABASE_URL=... python bank-website/db/seed_supabase.py      # 100 müştəri, RLS açıq, policy yox

## 2. R2
    npx wrangler r2 bucket create credit-risk-models
    bash deployment/upload_bundle.sh <model_version> credit-risk-models
R2 → Manage API tokens → S3 token (Object Read) → `R2_*` secret-ləri.

## 3. HF Space (Docker)
`deployment/hf-space/README.md`-ə bax. Secret/var-lar orada. `/health` → `{"model_loaded":true}` olana qədər gözlə.

## 4. Worker
    cd deployment/worker && npm install
    # wrangler.jsonc: ORIGIN_URL, ALLOWED_ORIGIN doldur
    npx wrangler deploy

## 5. Pages
Dashboard → Create → Pages → Git repo: Root `bank-website/frontend`, Build `npm run build`, Output `dist`,
env `VITE_API_URL=https://credit-risk-api.<acct>.workers.dev`. Sonra Worker `ALLOWED_ORIGIN` və Space `CORS_ORIGINS` = Pages URL, yenidən deploy.

## Checklist
Pre: [ ] `pytest tests -q` yaşıl [ ] `npm run build` keçir [ ] Supabase seed + RLS [ ] bundle R2-də [ ] secret-lər set, repo-da yox
 [ ] bundle approved deyilsə `ALLOW_DEV=1` və DEV xəbərdarlığı bilinir
Deploy: [ ] Space `/health` [ ] Worker `/health` [ ] Pages
Post (15 dəq): [ ] PIN `2QPR75P`(Low) `0JPKL0B`(Medium) `2H3TZR6`(High) [ ] yeni müraciət → təkrar PIN 409 [ ] brauzer CORS xətası yox
Rollback: `npx wrangler rollback`; Space-də əvvəlki commit; R2-də əvvəlki `models/<ver>` saxla.
Trigger: 5xx >2%, `model_loaded:false`, CORS xətası, isti p50 >3 s.
