"""Band threshold search on OOF only (decisions/0001). Output is a PROPOSAL, not business-approved."""
from __future__ import annotations

import numpy as np

from .risk_bands import band


def band_stats(y, p, low_max: float, medium_max: float) -> dict:
    """Per-band share, default rate, lift; plus High-as-positive confusion matrix."""
    y, p = np.asarray(y), np.asarray(p, float)
    labels = np.array([band(v, low_max, medium_max) for v in p])
    base = y.mean()
    out = {"low_max": low_max, "medium_max": medium_max, "bands": {}}
    for b in ("Low", "Medium", "High"):
        m = labels == b
        n = int(m.sum())
        rate = float(y[m].mean()) if n else float("nan")
        out["bands"][b] = {"n": n, "share": n / len(y), "default_rate": rate, "lift": rate / base if n else float("nan")}
    hi = labels == "High"
    tp, fp = int((hi & (y == 1)).sum()), int((hi & (y == 0)).sum())
    fn, tn = int((~hi & (y == 1)).sum()), int((~hi & (y == 0)).sum())
    out["confusion_high"] = {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
                             "precision": tp / (tp + fp) if tp + fp else float("nan"), "recall": tp / (tp + fn)}
    return out


def propose_thresholds(y, p, min_share: float = 0.10, low_shares=(0.3, 0.4, 0.5, 0.6),
                       high_shares=(0.10, 0.15, 0.2, 0.25)):
    """Grid over target band shares -> quantile thresholds. Picks max High/Low default-rate ratio
    subject to every band >= min_share. Returns (best, all_variants) sorted by ratio."""
    y, p = np.asarray(y), np.asarray(p, float)
    variants = []
    for ls in low_shares:
        for hs in high_shares:
            lo, md = float(np.quantile(p, ls)), float(np.quantile(p, 1 - hs))
            if not 0 <= lo < md <= 1:
                continue
            s = band_stats(y, p, lo, md)
            b = s["bands"]
            if min(v["share"] for v in b.values()) < min_share or b["Low"]["default_rate"] == 0:
                continue
            s["separation"] = b["High"]["default_rate"] / b["Low"]["default_rate"]
            variants.append(s)
    if not variants:
        raise ValueError("no threshold variant satisfies min_share")
    variants.sort(key=lambda s: -s["separation"])
    return variants[0], variants
