import numpy as np
import pytest

from src.evaluation.calibration import select_calibrator
from src.evaluation.metrics import bootstrap_auc_ci, calibration_metrics, discrimination, ece, reliability_table


def _data(n=4000, seed=0):
    rng = np.random.default_rng(seed)
    p_true = rng.beta(1, 12, n)
    y = (rng.random(n) < p_true).astype(int)
    return y, p_true


def test_discrimination_perfect_and_baseline():
    y = np.array([0, 0, 1, 1])
    d = discrimination(y, np.array([0.1, 0.2, 0.8, 0.9]))
    assert d["roc_auc"] == 1.0 and d["pr_auc"] == 1.0 and d["pr_auc_baseline"] == 0.5


def test_rejects_bad_input():
    with pytest.raises(ValueError):
        discrimination([0, 1], [0.5, 1.2])
    with pytest.raises(ValueError):
        discrimination([0, 2], [0.5, 0.2])


def test_reliability_and_ece():
    y, p = _data()
    t = reliability_table(y, p)
    assert len(t) == 10 and sum(r["n"] for r in t) == len(y)
    assert ece(y, p) < 0.02  # true probabilities are calibrated
    assert ece(y, np.clip(p * 3, 0, 1)) > ece(y, p)


def test_bootstrap_ci_contains_auc_and_is_seeded():
    y, p = _data()
    lo, hi = bootstrap_auc_ci(y, p, n_boot=200)
    assert lo < discrimination(y, p)["roc_auc"] < hi
    assert (lo, hi) == bootstrap_auc_ci(y, p, n_boot=200)


def test_calibrator_improves_miscalibrated():
    y, p = _data()
    raw = np.clip(p * 3, 0, 1)
    cal, info = select_calibrator(raw, y)
    assert info["chosen"] in ("platt", "isotonic")
    assert calibration_metrics(y, cal.predict(raw))["brier"] < info["raw"]["brier"]
    out = cal.predict(raw)
    assert ((out >= 0) & (out <= 1)).all()
