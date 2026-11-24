"""MOCK bundle (yalnız test/DEV). Real model deyil. Kontrakt: docs/contracts/model-bundle.md"""
import json
import sys
import types
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

FEATURES = ["ext_source_2", "credit_income_ratio", "days_employed"]


def install_band_stub() -> None:
    """05-in src/evaluation/risk_bands.py yoxdursa, YALNIZ testlər üçün stub. Real qayda 05-dədir."""
    try:
        import src.evaluation.risk_bands  # noqa: F401
        return
    except ImportError:
        pass
    mod = types.ModuleType("src.evaluation.risk_bands")
    mod.band = lambda p, low_max, medium_max: "Low" if p <= low_max else "Medium" if p <= medium_max else "High"
    sys.modules["src.evaluation.risk_bands"] = mod


def make_bundle(path: Path, status: str = "unvalidated", calibrated: bool = True, protected_key: bool = True,
                background: bool = True,
                business_approval: str = "approved", meta_calibrated: bool | None = None) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(42)
    X = pd.DataFrame(rng.normal(size=(500, len(FEATURES))), columns=FEATURES)
    y = (X.iloc[:, 1] - X.iloc[:, 0] + rng.normal(size=500) > 0).astype(int)
    model = Pipeline([("pre", ColumnTransformer([("num", SimpleImputer(), FEATURES)])), ("clf", LogisticRegression())]).fit(X, y)
    joblib.dump(model, path / "model.joblib")
    if background:
        X.sample(200, random_state=0).to_parquet(path / "background.parquet")
    if calibrated:
        raw = model.predict_proba(X)[:, 1]
        joblib.dump(IsotonicRegression(out_of_bounds="clip", y_min=0, y_max=1).fit(raw, y), path / "calibrator.joblib")
    (path / "feature_names.json").write_text(json.dumps(FEATURES))
    (path / "risk_policy.json").write_text(json.dumps(
        {"version": "mock", "low_max": 0.3, "medium_max": 0.6, "business_approval": business_approval}))
    meta = {
        "model_version": "mock-20260101-0000000", "algorithm": "logreg", "created_at": "2026-01-01T00:00:00Z",
        "feature_count": len(FEATURES), "metrics": {"roc_auc": 0.5}, "calibrated": calibrated if meta_calibrated is None else meta_calibrated,
        "validation_status": status, "risk_policy_version": "mock",
        "excluded_protected_features": ["code_gender"]}
    if not protected_key:
        del meta["excluded_protected_features"]
    (path / "metadata.json").write_text(json.dumps(meta))
    return path
