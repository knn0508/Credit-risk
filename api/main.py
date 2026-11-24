"""FastAPI tətbiqi. Başlatma: BUNDLE_DIR=artifacts/models/<ver> [ALLOW_DEV=1] uvicorn api.main:app"""
import logging
import os
import time

import uuid

from fastapi import FastAPI, HTTPException, Query

from api import service
from api.bundle import Bundle, BundleError, ExplainUnavailable, load_bundle
from api.schemas import (BatchRequest, BatchResponse, BatchRow, BatchSummary, RowError, ExplainResponse, ModelInfo,
                         Prediction, PredictRequest)

log = logging.getLogger("credit_api")  # giriş dəyərləri YAZILMIR


def _score_batch(b: Bundle, applicants: list[dict]) -> list[Prediction | None]:
    """Sürətli yol: bütün batch bir predict. Xəta olarsa pozuq sətirlər ucuz validasiya ilə tapılır,
    qalanları yenə bir dəfəyə skorlanır; hələ də xəta olarsa sətir-sətir. None = etibarsız sətir."""
    try:
        return list(service.score(b, applicants))
    except (ValueError, TypeError):
        pass
    good = [i for i, a in enumerate(applicants) if service.row_is_valid(b, a)]
    out: list[Prediction | None] = [None] * len(applicants)
    try:
        for i, p in zip(good, service.score(b, [applicants[i] for i in good])):
            out[i] = p
    except (ValueError, TypeError):
        for i in good:
            try:
                out[i] = service.score(b, [applicants[i]])[0]
            except (ValueError, TypeError):
                pass
    return out


def create_app(bundle: Bundle | None = None) -> FastAPI:
    app = FastAPI(title="Credit Risk Decision Support")
    state = {"bundle": bundle, "error": None}

    if bundle is None:
        path = os.environ.get("BUNDLE_DIR")
        try:
            if not path:
                raise BundleError("BUNDLE_DIR təyin olunmayıb")
            state["bundle"] = load_bundle(path, allow_dev=os.environ.get("ALLOW_DEV") == "1")
        except BundleError as e:
            state["error"] = str(e)

    def need() -> Bundle:
        if state["bundle"] is None:
            raise HTTPException(503, state["error"] or "bundle yoxdur")
        return state["bundle"]

    def score_one(b: Bundle, applicant: dict):
        """Tip/dəyər xətası → 422 (mesajda dəyər yoxdur)."""
        try:
            return service.score(b, [applicant])[0]
        except (ValueError, TypeError) as e:
            raise HTTPException(422, f"applicant dəyərləri etibarsızdır ({type(e).__name__})")

    def logged(preds: list[Prediction], t0: float) -> None:
        ms = (time.perf_counter() - t0) * 1000
        for p in preds:
            log.info("prediction_id=%s model_version=%s band=%s latency_ms=%.1f",
                     p.prediction_id, p.model_version, p.risk_band, ms)

    @app.get("/health")
    def health():
        return {"status": "ok", "model_loaded": state["bundle"] is not None}

    @app.get("/model-info", response_model=ModelInfo)
    def model_info():
        b = need()
        m = b.metadata
        return ModelInfo(
            model_version=m["model_version"], algorithm=m["algorithm"], created_at=m["created_at"],
            metrics=m.get("metrics", {}), risk_policy_version=b.risk_policy.get("version"),
            business_approval=b.risk_policy.get("business_approval"),
            validation_status=m["validation_status"], feature_count=m["feature_count"], feature_names=b.feature_names,
            excluded_protected_features=m.get("excluded_protected_features", []),
            dev_mode=b.dev_mode, warnings=b.warnings)

    @app.post("/predict", response_model=Prediction)
    def predict(req: PredictRequest):
        t0 = time.perf_counter()
        r = score_one(need(), req.applicant)
        logged([r], t0)
        return r

    @app.post("/predict/batch", response_model=BatchResponse)
    def batch(req: BatchRequest):
        t0 = time.perf_counter()
        b = need()
        rows: list[BatchRow] = []
        preds: list[Prediction] = []
        results = _score_batch(b, req.applicants)
        for i, p in enumerate(results):
            if p is None:  # dəyər mesaja yazılmır
                rows.append(BatchRow(index=i, status="error",
                                     error=RowError(code="VALIDATION", message="sətir dəyərləri etibarsızdır")))
            else:
                preds.append(p)
                rows.append(BatchRow(index=i, status="ok", prediction=p))
        logged(preds, t0)
        n_ok = len(preds)
        return BatchResponse(batch_id=str(uuid.uuid4()), results=rows,
                             summary=BatchSummary(total=len(rows), ok=n_ok, failed=len(rows) - n_ok))

    @app.post("/explain", response_model=ExplainResponse)
    def explain(req: PredictRequest, include_values: bool = False,
                top_n: int = Query(5, ge=1, le=10)):
        t0 = time.perf_counter()
        b = need()
        try:
            ex = b.explainer()
        except ExplainUnavailable as e:
            raise HTTPException(503, str(e))
        pred = score_one(b, req.applicant)
        X, _ = service.to_frame(b, [req.applicant])
        expl = ex.explain_row(X, top_n=top_n, include_values=include_values)  # fərdi izah loga yazılmır
        logged([pred], t0)
        return ExplainResponse(**pred.model_dump(), explanation=expl)

    return app


app = create_app()
