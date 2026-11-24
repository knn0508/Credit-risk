"""Pydantic schemas — docs/contracts/prediction-api.md v0.1 və explanation.md."""
from typing import Any, Optional
from pydantic import BaseModel, Field

DISCLAIMER = "Qərar dəstəyidir; avtomatik təsdiq/rədd deyil."
MAX_BATCH = 10_000


class PredictRequest(BaseModel):
    applicant: dict[str, Any]
    request_id: Optional[str] = None


class BatchRequest(BaseModel):
    applicants: list[dict[str, Any]] = Field(max_length=MAX_BATCH)


class Prediction(BaseModel):
    prediction_id: str
    timestamp: str
    model_version: str
    prediction_probability: float
    risk_band: str
    calibrated: bool
    warnings: list[str]
    disclaimer: str = DISCLAIMER


class Factor(BaseModel):
    feature_name: str
    display_name: str
    value: Optional[float] = None
    contribution: float


class Explanation(BaseModel):
    method: str
    base_value: float
    top_positive_factors: list[Factor]
    top_negative_factors: list[Factor]
    note: str


class ExplainResponse(Prediction):
    explanation: Explanation


class BatchResponse(BaseModel):
    results: list[Prediction]


class ModelInfo(BaseModel):
    model_version: str
    algorithm: str
    created_at: str
    metrics: dict[str, float]
    risk_policy_version: Optional[str]
    validation_status: str
    feature_count: int
    dev_mode: bool
