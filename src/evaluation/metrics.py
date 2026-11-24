"""Discrimination + calibration metrics (Agent 05). Evaluate on OOF/holdout only."""
from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def _arr(y, p):
    y, p = np.asarray(y), np.asarray(p, dtype=float)
    if y.shape != p.shape or y.ndim != 1:
        raise ValueError("y and p must be 1-D of equal length")
    if np.isnan(p).any() or (p < 0).any() or (p > 1).any():
        raise ValueError("p must be probabilities in [0, 1]")
    if not set(np.unique(y)) <= {0, 1}:
        raise ValueError("y must be binary 0/1")
    return y, p


def discrimination(y, p) -> dict:
    y, p = _arr(y, p)
    return {"roc_auc": float(roc_auc_score(y, p)), "pr_auc": float(average_precision_score(y, p)),
            "pr_auc_baseline": float(y.mean())}


def reliability_table(y, p, n_bins: int = 10):
    """Quantile bins -> list of dicts (n, mean_p, event_rate)."""
    y, p = _arr(y, p)
    order = np.argsort(p, kind="stable")
    out = []
    for idx in np.array_split(order, n_bins):
        if len(idx):
            out.append({"n": int(len(idx)), "mean_p": float(p[idx].mean()), "event_rate": float(y[idx].mean())})
    return out


def ece(y, p, n_bins: int = 10) -> float:
    t = reliability_table(y, p, n_bins)
    n = sum(r["n"] for r in t)
    return float(sum(r["n"] * abs(r["mean_p"] - r["event_rate"]) for r in t) / n)


def calibration_metrics(y, p) -> dict:
    y, p = _arr(y, p)
    return {"brier": float(brier_score_loss(y, p)), "ece": ece(y, p)}


def bootstrap_auc_ci(y, p, n_boot: int = 1000, seed: int = 42, alpha: float = 0.05):
    y, p = _arr(y, p)
    rng = np.random.default_rng(seed)
    n, vals = len(y), []
    while len(vals) < n_boot:
        i = rng.integers(0, n, n)
        if y[i].min() != y[i].max():
            vals.append(roc_auc_score(y[i], p[i]))
    lo, hi = np.quantile(vals, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)
