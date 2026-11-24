"""Risk band mapping (Agent 05). Single source of truth; API (06) imports `band`.

Rule (decisions/0001): p_cal <= low_max -> Low; p_cal <= medium_max -> Medium; else High.
Thresholds come from configs/risk_policy.yaml (status: proposal until 01 approves).
"""
from __future__ import annotations

import math
from typing import Mapping

LOW, MEDIUM, HIGH = "Low", "Medium", "High"


def validate_thresholds(low_max: float, medium_max: float) -> None:
    for name, v in (("low_max", low_max), ("medium_max", medium_max)):
        if v is None or not isinstance(v, (int, float)) or math.isnan(v):
            raise ValueError(f"{name} must be a number, got {v!r} (policy not set)")
        if not 0.0 <= v <= 1.0:
            raise ValueError(f"{name} must be in [0, 1], got {v}")
    if low_max >= medium_max:
        raise ValueError(f"low_max ({low_max}) must be < medium_max ({medium_max})")


def band(p_cal: float, low_max: float, medium_max: float) -> str:
    """Map a calibrated default probability to Low/Medium/High."""
    if p_cal is None or isinstance(p_cal, bool) or math.isnan(p_cal) or not 0.0 <= p_cal <= 1.0:
        raise ValueError(f"p_cal must be a probability in [0, 1], got {p_cal!r}")
    validate_thresholds(low_max, medium_max)
    if p_cal <= low_max:
        return LOW
    if p_cal <= medium_max:
        return MEDIUM
    return HIGH


def band_from_policy(p_cal: float, policy: Mapping) -> str:
    """policy: dict like risk_policy.json {low_max, medium_max} or {thresholds: {...}}."""
    t = policy.get("thresholds", policy)
    return band(p_cal, t["low_max"], t["medium_max"])
