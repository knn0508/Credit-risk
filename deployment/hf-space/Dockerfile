# Hugging Face Space (Docker SDK). Build konteksti: repo kökü. Streamlit/app daxil deyil. Bundle R2-dən start-da gəlir.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /srv
COPY deployment/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY api ./api
COPY src ./src
COPY configs/feature_display_names.yaml ./configs/feature_display_names.yaml
COPY deployment/hf-space/fetch_bundle.py ./fetch_bundle.py
RUN mkdir -p /models/current && useradd --uid 1000 --create-home appuser && chown -R appuser /models /srv
USER appuser
ENV BUNDLE_DIR=/models/current PYTHONUNBUFFERED=1
EXPOSE 7860
CMD ["sh", "-c", "python fetch_bundle.py && uvicorn api.main:app --host 0.0.0.0 --port 7860"]
