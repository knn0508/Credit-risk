#!/usr/bin/env bash
# HF Space repo-su üçün qovluq yığır: bash deployment/hf-space/stage.sh  → .hf-stage/ (sonra orada git init/push → Space remote)
set -euo pipefail
cd "$(dirname "$0")/../.."
rm -rf .hf-stage && mkdir -p .hf-stage/configs .hf-stage/deployment/hf-space
cp -r api src .hf-stage/
find .hf-stage -name __pycache__ -type d -prune -exec rm -rf {} +
cp configs/feature_display_names.yaml .hf-stage/configs/
cp deployment/requirements.txt .hf-stage/deployment/
cp deployment/hf-space/fetch_bundle.py .hf-stage/deployment/hf-space/
cp deployment/hf-space/Dockerfile deployment/hf-space/README.md .hf-stage/
echo ".hf-stage hazırdır"
