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
                metrics, positive_rate, excluded_protected_features=(), preprocessor=None):
    import numpy, pandas, sklearn
    sha, today = git_sha(), datetime.now(timezone.utc)
    version = f"{algorithm}-{today:%Y%m%d}-{sha}"
    d = Path(root) / version
    d.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, d / "model.joblib")
    joblib.dump(preprocessor, d / "preprocessor.joblib")  # Pipeline daxilindədirsə None
    (d / "feature_names.json").write_text(json.dumps(list(feature_names)))
    (d / "split.json").write_text(json.dumps(split))
    oof.to_parquet(d / "oof_predictions.parquet", index=False)
    meta = {"model_version": version, "algorithm": algorithm, "created_at": today.isoformat(), "git_sha": sha,
            "seed": seed, "config_path": config_path, "data_version": data_version,
            "train_rows": len(oof), "positive_rate": positive_rate, "feature_count": len(feature_names),
            "metrics": metrics, "calibrated": False, "validation_status": "unvalidated", "approved_by": None,
            "risk_policy_version": None, "excluded_protected_features": list(excluded_protected_features),
            "library_versions": {"numpy": numpy.__version__, "pandas": pandas.__version__,
                                 "scikit-learn": sklearn.__version__}}
    (d / "metadata.json").write_text(json.dumps(meta, indent=2))
    return d


def load_bundle(path):
    d = Path(path)
    meta = json.loads((d / "metadata.json").read_text())
    names = json.loads((d / "feature_names.json").read_text())
    return joblib.load(d / "model.joblib"), names, meta
