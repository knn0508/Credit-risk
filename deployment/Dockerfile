# Build konteksti: repo kökü. Bundle image-ə QOYULMUR — volume kimi qoşulur.
FROM python:3.12-slim
WORKDIR /srv
RUN pip install --no-cache-dir fastapi uvicorn pydantic joblib numpy pandas scikit-learn lightgbm xgboost catboost shap streamlit httpx pyyaml
COPY api ./api
COPY src ./src
COPY app ./app
ENV BUNDLE_DIR=/models/current
EXPOSE 8000 8501
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
