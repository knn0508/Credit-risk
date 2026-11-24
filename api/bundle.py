"""Bundle yükləmə — docs/contracts/model-bundle.md. Band qaydası src/evaluation/risk_bands.py-dadır (05)."""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import joblib


class BundleError(Exception):
    """Bundle yoxdur, natamamdır və ya təsdiqsizdir (→ 503)."""


@dataclass
class Bundle:
    model: Any
    calibrator: Optional[Any]
    feature_names: list[str]
    metadata: dict
    risk_policy: dict
    dev_mode: bool

    @property
    def warnings(self) -> list[str]:
        # açar yoxdur ≠ açar boş siyahıdır
        if "excluded_protected_features" not in self.metadata:
            return ["excluded_protected_features metadata-da yoxdur"]
        return []


def load_bundle(path: str | os.PathLike, allow_dev: bool = False) -> Bundle:
    p = Path(path)
    try:
        meta = json.loads((p / "metadata.json").read_text())
        names = json.loads((p / "feature_names.json").read_text())
        policy = json.loads((p / "risk_policy.json").read_text())
        model = joblib.load(p / "model.joblib")
    except (OSError, ValueError) as e:
        raise BundleError(f"bundle oxunmadı: {p}: {e}") from e
    cal_path = p / "calibrator.joblib"
    calibrator = joblib.load(cal_path) if cal_path.exists() else None

    if meta.get("feature_count") != len(names):
        raise BundleError("feature_names və metadata.feature_count uyğun deyil")
    approved = meta.get("validation_status") == "approved"
    if approved and "excluded_protected_features" not in meta:
        raise BundleError("təsdiqli bundle-da excluded_protected_features açarı yoxdur")
    if not approved and not allow_dev:
        raise BundleError(
            f"bundle təsdiqsizdir (status={meta.get('validation_status')}); DEV rejimi söndürülüb")
    return Bundle(model, calibrator, names, meta, policy, dev_mode=not approved)
