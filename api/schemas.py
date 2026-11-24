"""Pydantic schemas — docs/contracts/prediction-api.md v0.1 və explanation.md."""
from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

DISCLAIMER = ("Qərar dəstəyidir; avtomatik təsdiq/rədd deyil. "
              "Yalnız demo/prototip; real kredit qərarları üçün deyil.")
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
    value: Optional[Any] = None
    contribution: float


class Explanation(BaseModel):
    method: str
    explanation_space: Literal["log_odds", "probability"] = "log_odds"
    base_value: float
    top_positive_factors: list[Factor]
    top_negative_factors: list[Factor]
    note: str


class ExplainResponse(Prediction):
    explanation: Explanation


class RowError(BaseModel):
    code: str
    message: str


class BatchRow(BaseModel):
    index: int
    status: Literal["ok", "error"]
    prediction: Optional[Prediction] = None
    error: Optional[RowError] = None


class BatchSummary(BaseModel):
    total: int
    ok: int
    failed: int


class BatchResponse(BaseModel):
    batch_id: str
    results: list[BatchRow]
    summary: BatchSummary


class ModelInfo(BaseModel):
    model_version: str
    algorithm: str
    created_at: str
    metrics: dict[str, float]
    risk_policy_version: Optional[str]
    business_approval: Optional[str] = None
    validation_status: str
    feature_count: int
    feature_names: list[str]
    excluded_protected_features: list[str]
    dev_mode: bool
    warnings: list[str] = []
