#!/usr/bin/env bash
# Runtime bundle fayllarını R2-yə yükləyir: bash deployment/upload_bundle.sh <model_version> <bucket>
set -euo pipefail
V="$1"; B="$2"
cd "$(dirname "$0")/../artifacts/models/$V"
for f in model.joblib calibrator.joblib feature_names.json metadata.json risk_policy.json background.parquet; do
  npx wrangler r2 object put "$B/models/$V/$f" --file "$f" --remote
done
