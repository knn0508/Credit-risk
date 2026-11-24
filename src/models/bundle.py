"""Model bundle (contracts/model-bundle.md v0.1). calibrator=None, validation_status=unvalidated."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import joblib


def file_hash(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]


def data_version(schema_path="data/processed/schema.json") -> str:
    """02-nin data versiyası (schema.json meta.data_version, raw fayl hash-lərindən)."""
    return json.loads(Path(schema_path).read_text())["meta"]["data_version"]


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short=7", "HEAD"], text=True).strip()
    except Exception:
        return "nogit00"


def save_bundle(root, model, feature_names, oof, split, *, algorithm, seed, config_path, data_version,
                metrics, positive_rate, X_train, excluded_protected_features=(), excluded_drift_features=(), device="cpu", extra_excluded_features=(), preprocessor=None):
    import importlib.metadata as im
    import numpy, pandas, sklearn
    libs = {"numpy": numpy.__version__, "pandas": pandas.__version__, "scikit-learn": sklearn.__version__}
    for lib in ("lightgbm", "xgboost", "catboost"):
        try:
            libs[lib] = im.version(lib)
        except im.PackageNotFoundError:
            pass
    sha, today = git_sha(), datetime.now(timezone.utc)
    version = f"{algorithm}-{today:%Y%m%d}-{sha}"
    d = Path(root) / version
    d.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, d / "model.joblib")
    joblib.dump(preprocessor, d / "preprocessor.joblib")  # Pipeline daxilindədirsə None
    (d / "feature_names.json").write_text(json.dumps(list(feature_names)))
    (d / "split.json").write_text(json.dumps(split))
    oof.to_parquet(d / "oof_predictions.parquet", index=False)
    # SHAP background (06 /explain): train-dən ≤1000 sətir, seed ilə; real sətirlər → yalnız artifacts/, loglanmır
    X_train[list(feature_names)].sample(n=min(1000, len(X_train)), random_state=seed).reset_index(drop=True) \
        .to_parquet(d / "background.parquet", index=False)
    meta = {"model_version": version, "algorithm": algorithm, "created_at": today.isoformat(), "git_sha": sha,
            "seed": seed, "config_path": config_path, "data_version": data_version,
            "train_rows": len(oof), "positive_rate": positive_rate, "feature_count": len(feature_names),
            "metrics": metrics, "calibrated": False, "validation_status": "unvalidated", "approved_by": None,
            "risk_policy_version": None, "excluded_protected_features": list(excluded_protected_features),
            "excluded_drift_features": list(excluded_drift_features), "excluded_drift_decision": "decisions/0003", "extra_excluded_features": list(extra_excluded_features),
            "device": device if algorithm.split("-")[0] in ("xgb", "catboost") else "cpu", "library_versions": libs}
    (d / "metadata.json").write_text(json.dumps(meta, indent=2))
    return d


def load_bundle(path):
    d = Path(path)
    meta = json.loads((d / "metadata.json").read_text())
    names = json.loads((d / "feature_names.json").read_text())
    return joblib.load(d / "model.joblib"), names, meta
