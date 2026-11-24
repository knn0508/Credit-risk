"""Subgroup audit (statistical, not proof of fairness). Protected attrs are NOT model features (decisions/0002)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .metrics import discrimination
from .risk_bands import band

MIN_N, MIN_POS = 100, 10


def age_groups(days_birth: pd.Series) -> pd.Series:
    """days_birth is negative (days before application)."""
    years = -days_birth / 365.25
    return pd.cut(years, [0, 30, 40, 50, 60, 200], right=False,
                  labels=["<30", "30-39", "40-49", "50-59", "60+"]).astype("object")


def audit(df: pd.DataFrame, group_col: str, low_max: float, medium_max: float) -> pd.DataFrame:
    """df needs target, p_cal, group_col. NaN group -> 'unknown'. Small groups: auc='insufficient'."""
    g = df[group_col].astype("object").where(df[group_col].notna(), "unknown")
    base = df.target.mean()
    rows = []
    for name, d in df.groupby(g):
        n, pos = len(d), int(d.target.sum())
        ok = n >= MIN_N and pos >= MIN_POS and pos < n
        high = np.mean([band(v, low_max, medium_max) == "High" for v in d.p_cal])
        rows.append({"group": name, "n": n, "default_rate": pos / n, "mean_p_cal": float(d.p_cal.mean()),
                     "calib_gap": float(d.p_cal.mean() - d.target.mean()),
                     "high_share": float(high), "auc": discrimination(d.target, d.p_cal)["roc_auc"] if ok else "insufficient",
                     "default_vs_base": pos / n / base})
    return pd.DataFrame(rows).sort_values("group").reset_index(drop=True)
