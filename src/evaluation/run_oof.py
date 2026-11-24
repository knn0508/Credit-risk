"""OOF-only validation step: calibrator + threshold proposal. Does NOT touch holdout.
Usage: python -m src.evaluation.run_oof artifacts/models/<version>
Writes <bundle>/calibrator.joblib and reports/oof_<version>.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import pandas as pd

from .calibration import select_calibrator
from .cost import cost_sensitivity
from .metrics import bootstrap_auc_ci, discrimination, reliability_table
from .thresholds import propose_thresholds


def main(bundle: str) -> dict:
    b = Path(bundle)
    oof = pd.read_parquet(b / "oof_predictions.parquet")
    split = json.loads((b / "split.json").read_text())
    assert oof.sk_id_curr.is_unique, "duplicate ids in OOF"
    assert not set(oof.sk_id_curr) & set(split["holdout_ids"]), "OOF overlaps holdout"
    y, p = oof.target.to_numpy(), oof.p_raw.to_numpy()
    cal, cmp_ = select_calibrator(p, y, seed=split.get("seed", 42))
    pc = cal.predict(p)
    best, variants = propose_thresholds(y, pc)
    res = {"model_version": b.name, "n_oof": len(oof), "base_rate": float(y.mean()),
           "discrimination_raw": discrimination(y, p), "auc_ci95": bootstrap_auc_ci(y, p),
           "calibration": cmp_, "reliability_raw": reliability_table(y, p),
           "reliability_cal": reliability_table(y, pc),
           "proposal": best, "variants": variants, "cost_sensitivity_ASSUMPTION": cost_sensitivity(y, pc)}
    joblib.dump(cal, b / "calibrator.joblib")
    out = Path("reports") / f"oof_{b.name}.json"
    out.write_text(json.dumps(res, indent=2))
    return res


if __name__ == "__main__":
    r = main(sys.argv[1])
    print(json.dumps({k: r[k] for k in ("n_oof", "discrimination_raw", "auc_ci95", "proposal")}, indent=1, default=str)[:2500])
    print({k: v for k, v in r["calibration"].items()})
