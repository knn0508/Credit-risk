"""Bundle yükləmə — docs/contracts/model-bundle.md. Band qaydası src/evaluation/risk_bands.py-dadır (05)."""
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

import joblib


class ExplainUnavailable(Exception):
    """İzah qurula bilmir (→ 503)."""


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
    path: Optional[Path] = None
    _explainer: Any = None

    def explainer(self):
        """Lazy ShapExplainer (src/explainability, 05). background.parquet yoxdursa/uyğunsuzdursa ExplainUnavailable."""
        if self._explainer is None:
            self._explainer = _build_explainer(self)
        return self._explainer

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
    return Bundle(model, calibrator, names, meta, policy, dev_mode=not approved, path=p)


def _build_explainer(b: Bundle):
    import pandas as pd
    from src.explainability.shap_explainer import ShapExplainer, load_display_names
    bg_path = b.path / "background.parquet" if b.path else None
    if bg_path is None or not bg_path.exists():
        raise ExplainUnavailable("bundle-da background.parquet yoxdur")
    bg = pd.read_parquet(bg_path)
    if list(bg.columns) != b.feature_names:
        raise ExplainUnavailable("background sütunları feature_names ilə uyğun deyil")
    try:
        return ShapExplainer(b.model, bg, load_display_names())
    except (KeyError, AttributeError, ValueError) as e:
        raise ExplainUnavailable(f"model izah üçün uyğun deyil: {type(e).__name__}") from e
