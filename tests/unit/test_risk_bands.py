import math

import pytest

from src.evaluation.risk_bands import band, band_from_policy, HIGH, LOW, MEDIUM


def test_boundaries_inclusive_upper():
    assert band(0.0, 0.05, 0.15) == LOW
    assert band(0.05, 0.05, 0.15) == LOW
    assert band(0.0500001, 0.05, 0.15) == MEDIUM
    assert band(0.15, 0.05, 0.15) == MEDIUM
    assert band(0.1500001, 0.05, 0.15) == HIGH
    assert band(1.0, 0.05, 0.15) == HIGH


@pytest.mark.parametrize("p", [-0.1, 1.1, float("nan"), None])
def test_invalid_probability(p):
    with pytest.raises(ValueError):
        band(p, 0.05, 0.15)


@pytest.mark.parametrize("lo,hi", [(0.2, 0.1), (0.1, 0.1), (None, 0.1), (0.1, 1.5), (-0.1, 0.5)])
def test_invalid_thresholds(lo, hi):
    with pytest.raises(ValueError):
        band(0.1, lo, hi)


def test_policy_forms():
    assert band_from_policy(0.1, {"low_max": 0.05, "medium_max": 0.15}) == MEDIUM
    assert band_from_policy(0.1, {"thresholds": {"low_max": 0.05, "medium_max": 0.15}}) == MEDIUM
    with pytest.raises(ValueError):  # unset proposal policy must not silently classify
        band_from_policy(0.1, {"thresholds": {"low_max": None, "medium_max": None}})
