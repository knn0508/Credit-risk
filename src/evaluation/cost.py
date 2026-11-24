"""Cost sensitivity. FN:FP cost ratios are ASSUMPTIONS, not real business costs."""
from __future__ import annotations

import numpy as np


def cost_at_threshold(y, p, threshold: float, fn_cost: float, fp_cost: float = 1.0) -> dict:
    y, p = np.asarray(y), np.asarray(p, float)
    flag = p > threshold
    fn = int(((~flag) & (y == 1)).sum())
    fp = int((flag & (y == 0)).sum())
    total = fn * fn_cost + fp * fp_cost
    return {"threshold": float(threshold), "fn": fn, "fp": fp, "total_cost": float(total),
            "cost_per_application": float(total / len(y))}


def cost_sensitivity(y, p, ratios=(2, 3, 5, 8, 10), grid=None) -> list[dict]:
    """For each assumed FN:FP ratio, the cost-minimising threshold over a grid. Label: assumption."""
    y, p = np.asarray(y), np.asarray(p, float)
    grid = np.quantile(p, np.linspace(0.05, 0.99, 95)) if grid is None else np.asarray(grid)
    rows = []
    for r in ratios:
        best = min((cost_at_threshold(y, p, t, r) for t in grid), key=lambda c: c["total_cost"])
        no_model = float((y == 1).sum() * r)  # approve everyone: every default is a FN
        rows.append({"fn_fp_ratio": r, "assumption": True, **best,
                     "cost_flag_none": no_model, "saving_vs_flag_none": no_model - best["total_cost"]})
    return rows
