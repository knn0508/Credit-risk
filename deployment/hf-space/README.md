---
title: Credit Risk API
sdk: docker
app_port: 7860
pinned: false
---
# HF Space — Credit Risk API (FastAPI)
Bu fayl Space repo-nun README.md-si kimi istifadə olunur (YAML başlıq HF üçün).

## Space-ə push
    bash deployment/hf-space/stage.sh                # .hf-stage/ yığır (api, src, configs, Dockerfile, README)
    cd .hf-stage && git init -b main && git add . && git commit -m "deploy"
    git remote add space https://huggingface.co/spaces/<user>/<space> && git push -f space main
Space repo-su ayrıdır; secret-lər Dockerfile/kodda yoxdur, yalnız Space Settings-də.

## Space Settings → Secrets / Variables
Secrets: `DATABASE_URL` (Supabase pooler URI), `R2_ACCOUNT_ID`, `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`, `MODEL_VERSION`
Variables: `CORS_ORIGINS` (Worker origin-i boş qoyma: Worker server-to-server çağırır, brauzer yox — `https://<project>.pages.dev` yaz),
`ALLOW_DEV=1` (bundle `approved` olmadıqda).
