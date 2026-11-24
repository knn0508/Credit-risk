import numpy as np
import pytest

from src.evaluation.cost import cost_at_threshold, cost_sensitivity
from src.evaluation.thresholds import band_stats, propose_thresholds


def _data(n=20000, seed=1):
    rng = np.random.default_rng(seed)
    p = rng.beta(1, 11, n)
    return (rng.random(n) < p).astype(int), p


def test_band_stats_partition_and_confusion():
    y, p = _data()
    s = band_stats(y, p, 0.05, 0.15)
    assert sum(b["n"] for b in s["bands"].values()) == len(y)
    c = s["confusion_high"]
    assert c["tp"] + c["fp"] + c["fn"] + c["tn"] == len(y)
    assert c["tp"] + c["fn"] == y.sum()
    assert s["bands"]["Low"]["default_rate"] < s["bands"]["High"]["default_rate"]


def test_boundary_is_low_inclusive():
    s = band_stats(np.array([0, 1, 1]), np.array([0.1, 0.2, 0.3]), 0.1, 0.2)
    assert [s["bands"][b]["n"] for b in ("Low", "Medium", "High")] == [1, 1, 1]


def test_propose_respects_min_share_and_orders():
    y, p = _data()
    best, allv = propose_thresholds(y, p)
    assert best["low_max"] < best["medium_max"]
    assert all(min(b["share"] for b in v["bands"].values()) >= 0.10 for v in allv)
    seps = [v["separation"] for v in allv]
    assert seps == sorted(seps, reverse=True) and best["separation"] > 1


def test_propose_fails_when_impossible():
    with pytest.raises(ValueError):
        propose_thresholds(np.array([0, 1] * 50), np.full(100, 0.5))


def test_cost_arithmetic_and_sensitivity():
    y, p = np.array([1, 0, 1, 0]), np.array([0.9, 0.8, 0.1, 0.1])
    c = cost_at_threshold(y, p, 0.5, fn_cost=5)
    assert (c["fn"], c["fp"], c["total_cost"]) == (1, 1, 6.0)
    rows = cost_sensitivity(*_data(), ratios=(2, 10))
    assert all(r["assumption"] and r["saving_vs_flag_none"] >= 0 for r in rows)
    assert rows[1]["threshold"] <= rows[0]["threshold"]  # higher FN cost -> lower threshold
