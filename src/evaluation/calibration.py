"""Calibrators fit on OOF only (decisions/0001). Interface: predict(p_raw) -> p_cal."""
from __future__ import annotations

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold

from .metrics import calibration_metrics


class PlattCalibrator:
    def fit(self, p_raw, y):
        p = np.clip(np.asarray(p_raw, float), 1e-6, 1 - 1e-6)
        self._lr = LogisticRegression(C=1e6).fit(np.log(p / (1 - p)).reshape(-1, 1), y)
        return self

    def predict(self, p_raw):
        p = np.clip(np.asarray(p_raw, float), 1e-6, 1 - 1e-6)
        return self._lr.predict_proba(np.log(p / (1 - p)).reshape(-1, 1))[:, 1]


class IsotonicCalibrator:
    def fit(self, p_raw, y):
        self._iso = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0).fit(p_raw, y)
        return self

    def predict(self, p_raw):
        return self._iso.predict(np.asarray(p_raw, float))


METHODS = {"platt": PlattCalibrator, "isotonic": IsotonicCalibrator}


def select_calibrator(p_raw, y, seed: int = 42, n_splits: int = 5):
    """CV on OOF predictions; pick lowest mean Brier. Returns (fitted calibrator, comparison dict)."""
    p_raw, y = np.asarray(p_raw, float), np.asarray(y)
    skf = StratifiedKFold(n_splits, shuffle=True, random_state=seed)
    res = {"raw": calibration_metrics(y, p_raw)}
    for name, cls in METHODS.items():
        pc = np.empty_like(p_raw)
        for tr, te in skf.split(p_raw, y):
            pc[te] = cls().fit(p_raw[tr], y[tr]).predict(p_raw[te])
        res[name] = calibration_metrics(y, pc)
    best = min(METHODS, key=lambda k: res[k]["brier"])
    return METHODS[best]().fit(p_raw, y), {"chosen": best, **res}
