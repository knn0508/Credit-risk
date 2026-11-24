"""Skorlama məntiqi. Feature/preprocessing məntiqi təkrarlanmır: bundle-dakı model Pipeline-dır."""
import uuid
from datetime import datetime, timezone

import pandas as pd

from api.bundle import Bundle
from api.schemas import Prediction


def _band(p: float, policy: dict) -> str:
    # Qayda 05-in src/evaluation/risk_bands.py funksiyasındadır; burada özbaşına yazılmır.
    from src.evaluation.risk_bands import band
    return band(p, policy["low_max"], policy["medium_max"])


def to_frame(b: Bundle, applicants: list[dict]) -> tuple[pd.DataFrame, list[list[str]]]:
    """Sütunları feature_names sırasına salır; çatışan → NaN+warning, naməlum → ignore+warning."""
    known = set(b.feature_names)
    rows, warns = [], []
    for a in applicants:
        w = []
        missing = [f for f in b.feature_names if f not in a]
        unknown = [k for k in a if k not in known and k != "SK_ID_CURR"]
        if missing:
            w.append(f"{len(missing)} çatışmayan sahə null qəbul edildi")
        if unknown:
            w.append(f"{len(unknown)} naməlum sahə nəzərə alınmadı")
        rows.append({f: a.get(f) for f in b.feature_names})
        warns.append(w)
    return pd.DataFrame(rows, columns=b.feature_names), warns


def score(b: Bundle, applicants: list[dict]) -> list[Prediction]:
    X, warns = to_frame(b, applicants)
    p = b.model.predict_proba(X)[:, 1]
    calibrated = b.calibrator is not None
    if calibrated:
        p = b.calibrator.predict(p)
    now = datetime.now(timezone.utc).isoformat()
    out = []
    for pi, w in zip(p, warns):
        w = list(w) + b.warnings
        if not calibrated:
            w.append("calibrator yoxdur: xam ehtimal istifadə olunur")
        if b.dev_mode:
            w.append("DEV rejimi: bundle təsdiqlənməyib")
        out.append(Prediction(
            prediction_id=str(uuid.uuid4()), timestamp=now,
            model_version=b.metadata["model_version"],
            prediction_probability=float(pi), risk_band=_band(float(pi), b.risk_policy),
            calibrated=calibrated, warnings=w))
    return out
