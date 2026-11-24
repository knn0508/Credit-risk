# Build konteksti: repo kökü (docker compose -f deployment/docker-compose.yml build).
# Bundle image-ə QOYULMUR — /models/current-ə read-only volume kimi qoşulur.
FROM python:3.12-slim
# lightgbm/xgboost/catboost üçün OpenMP runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
COPY deployment/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./api
COPY src ./src
COPY app ./app
COPY configs/feature_display_names.yaml ./configs/feature_display_names.yaml
COPY docs/data/sample-applicants.json ./docs/data/sample-applicants.json
RUN useradd --uid 10001 --no-create-home appuser
USER appuser
ENV BUNDLE_DIR=/models/current PYTHONUNBUFFERED=1
EXPOSE 8000 8501
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health',timeout=3).status==200 else 1)"
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
