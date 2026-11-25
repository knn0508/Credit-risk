# Demo Bank website

Landing page → "Request credit" → enter 7-character PIN → risk band + top factors. Demo only; decision support, not approval.

```
bank-website/
  db/build_db.py         # builds db/bank.db: 100 customers (PIN + all processed features)
  frontend/              # Vite + React + Tailwind v4
  design-system/         # ui-ux-pro-max design system (MASTER.md)
  .design/DESIGN_REVIEW.md
```

API endpoint `POST /bank/credit-check` lives in `api/` (see `docs/contracts/prediction-api.md`).

## Run (3 terminals from repo root)
```bash
python bank-website/db/build_db.py            # once (deterministic, seed 42)
BUNDLE_DIR=artifacts/models/<version> ALLOW_DEV=1 uvicorn api.main:app --port 8000
cd bank-website/frontend && npm install && npm run dev   # http://localhost:5173
```
Vite proxies `/bank/*` to `http://127.0.0.1:8000` (override with `API_URL`).

PIN rule: exactly 7 chars, `A-Z0-9`, at least one letter and one digit. Sample PINs: `2QPR75P` (Low), `0JPKL0B` (Medium), `2H3TZR6` (High).
