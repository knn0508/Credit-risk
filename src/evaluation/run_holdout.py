"""FINAL holdout report: thresholds are FROZEN from OOF (reports/oof_<version>.json), holdout used once.
Usage: python -m src.evaluation.run_holdout artifacts/models/<version>
Scores holdout with the bundle model + OOF-fitted calibrator, applies frozen bands, runs subgroup audit and
SHAP global importance (CPU, 5000-row holdout sample). Writes reports/holdout_<version>.json and
reports/subgroups_<version>_holdout.md. Never logs individual applicants.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from src.explainability.shap_explainer import ShapExplainer, load_display_names
from src.models import protocol
from src.models.train_baseline import load_xy

from .metrics import bootstrap_auc_ci, calibration_metrics, discrimination, reliability_table
from .risk_bands import bands
from .run_audit import COLS, to_md
from .subgroups import age_groups, audit


def main(bundle: str) -> dict:
    b = Path(bundle)
    oof_rep = json.loads((Path("reports") / f"oof_{b.name}.json").read_text())
    lo, hi = oof_rep["proposal"]["low_max"], oof_rep["proposal"]["medium_max"]
    split = json.loads((b / "split.json").read_text())
    names = json.loads((b / "feature_names.json").read_text())
    model, cal = joblib.load(b / "model.joblib"), joblib.load(b / "calibrator.joblib")
    cfg = protocol.load_config(protocol.DEFAULT_CONFIG)
    X, y, ids = load_xy(cfg)
    ho_ids = set(split["holdout_ids"])
    assert not ho_ids & set(split["train_ids"]), "split overlap"
    m = ids.isin(ho_ids).to_numpy()
    X, y, ids = X[m], y[m], ids[m]
    assert len(X) == len(ho_ids) and ids.is_unique
    assert list(X.columns) == names or set(X.columns) >= set(names), "feature mismatch"
    X = X[names]
    p_raw = model.predict_proba(X)[:, 1]
    p = cal.predict(p_raw)
    yy = y.to_numpy()
    bd = np.array(bands(p, lo, hi))
    tab = {k: {"n": int((bd == k).sum()), "share": float((bd == k).mean()),
               "default_rate": float(yy[bd == k].mean()), "lift": float(yy[bd == k].mean() / yy.mean())}
           for k in ("Low", "Medium", "High")}
    hi_m = bd == "High"
    tp, fp = int((yy[hi_m] == 1).sum()), int((yy[hi_m] == 0).sum())
    fn = int((yy[~hi_m] == 1).sum())
    res = {"model_version": b.name, "n_holdout": len(yy), "base_rate": float(yy.mean()),
           "thresholds_frozen_from_oof": {"low_max": lo, "medium_max": hi},
           "discrimination_raw": discrimination(yy, p_raw), "discrimination_cal": discrimination(yy, p),
           "auc_ci95": bootstrap_auc_ci(yy, p), "calibration_cal": calibration_metrics(yy, p),
           "reliability_cal": reliability_table(yy, p), "bands": tab,
           "high": {"tp": tp, "fp": fp, "fn": fn, "precision": tp / max(tp + fp, 1), "recall": tp / max(tp + fn, 1)}}
    # subgroup audit (holdout)
    d = pd.read_parquet("data/processed/application_train.parquet", columns=["sk_id_curr", *COLS])
    df = pd.DataFrame({"sk_id_curr": ids.to_numpy(), "target": yy, "p_cal": p, "p_raw": p_raw})
    df = df.merge(d, on="sk_id_curr", how="left", validate="1:1")
    df["age_group"] = age_groups(df.days_birth)
    df["children_group"] = df.cnt_children.clip(upper=3).astype("Int64").astype(str).replace("3", "3+")
    parts = [f"# Subgroup audit — {b.name} (holdout, hədlər OOF-dan dondurulub)\n"]
    for g in ["code_gender", "age_group", "name_education_type", "name_family_status", "occupation_type",
              "organization_type", "region_rating_client", "children_group"]:
        parts.append(f"\n## {g}\n\n" + audit(df, g, lo, hi).round(4).pipe(to_md) + "\n")
    Path("reports", f"subgroups_{b.name}_holdout.md").write_text("\n".join(parts), encoding="utf-8")
    # SHAP global (CPU)
    bg = pd.read_parquet(b / "background.parquet")
    ex = ShapExplainer(model, bg[names] if set(names) <= set(bg.columns) else bg, load_display_names())
    imp = ex.global_importance(X.sample(5000, random_state=42))
    res["shap_method"] = ex.method
    res["shap_top25_mean_abs_log_odds"] = {k: float(v) for k, v in imp.head(25).items()}
    Path("reports", f"holdout_{b.name}.json").write_text(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    r = main(sys.argv[1])
    print(json.dumps({k: r[k] for k in ("n_holdout", "discrimination_raw", "discrimination_cal", "auc_ci95",
                                         "calibration_cal", "bands", "high")}, indent=1))
    print(json.dumps(r["shap_top25_mean_abs_log_odds"], indent=1))
