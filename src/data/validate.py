"""Single-applicant validation against docs/data/sample-schema.json (for API/UI; prediction-api.md rules).

validate_applicant(applicant) -> ValidationResult
  errors   : type / allowed-value violations  -> API answers 422
  warnings : missing field (-> null), unknown field (ignored), value outside train range
  cleaned  : dict with every schema field; missing -> None, unknown dropped (use only if `ok`)
No raw values are logged or put into messages beyond the field name (sensitive applicant data).
"""
import json
import math
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

DEFAULT_SCHEMA = Path(__file__).resolve().parents[2] / "docs" / "data" / "sample-schema.json"


@dataclass
class ValidationResult:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    cleaned: dict = field(default_factory=dict)

    @property
    def ok(self):
        return not self.errors


@lru_cache(maxsize=4)
def load_schema(path=str(DEFAULT_SCHEMA)):
    fields = json.loads(Path(path).read_text(encoding="utf-8"))["fields"]
    return {f["name"]: f for f in fields}


def _is_number(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_applicant(applicant, schema=None):
    spec = schema or load_schema()
    res = ValidationResult()
    if not isinstance(applicant, dict):
        res.errors.append("applicant must be an object {feature_name: value}")
        return res
    for name in applicant:
        if name not in spec:
            res.warnings.append(f"unknown field ignored: {name}")
    for name, f in spec.items():
        if name not in applicant or applicant[name] is None:
            if name in applicant and not f["nullable"]:
                res.warnings.append(f"{name}: null given but never null in training data")
            elif name not in applicant:
                res.warnings.append(f"missing field set to null: {name}")
            res.cleaned[name] = None
            continue
        v, kind = applicant[name], f["kind"]
        if kind == "categorical":
            if not isinstance(v, str):
                res.errors.append(f"{name}: expected string")
            elif v not in f["allowed_values"]:
                res.errors.append(f"{name}: value not in allowed values")
        elif kind == "binary":
            if isinstance(v, bool) or not _is_number(v) or v not in (0, 1):
                res.errors.append(f"{name}: expected 0 or 1")
        else:  # integer / float
            if not _is_number(v) or (isinstance(v, float) and not math.isfinite(v)):
                res.errors.append(f"{name}: expected a finite number")
            elif kind == "integer" and v != int(v):
                res.errors.append(f"{name}: expected an integer")
            elif not f["min"] <= v <= f["max"]:
                res.warnings.append(f"{name}: outside range seen in training data")
        res.cleaned[name] = v
    return res
