"""Class weight müqayisəsi + məhdud random-search tuning (config: tuning). Yalnız train hissəsi, holdout-a TOXUNMUR.
python -m src.models.tune  → artifacts/models/tuning_results.json (ən yaxşı params; configs-ə əllə köçürülür)"""
import json
import time
from pathlib import Path

import pandas as pd
from sklearn.model_selection import ParameterSampler

from . import benchmark, cv, protocol
from .train_baseline import load_xy


def main(config: str = protocol.DEFAULT_CONFIG):
    cfg = protocol.load_config(config)
    t, seed = cfg["tuning"], cfg["random_seed"]
    X, y, ids = load_xy(cfg)
    split = protocol.make_split(ids, y, seed, cfg["holdout_size"])
    tr = ids.isin(set(split["train_ids"])).to_numpy()
    Xt, yt, it = X[tr].reset_index(drop=True), y[tr].reset_index(drop=True), ids[tr].reset_index(drop=True)
    name, rows = t["model"], []

    def trial(params, label):
        t0 = time.time()
        _, m, pf = cv.run_cv(benchmark.make(name, Xt, seed, params), Xt, yt, it, seed, cfg["cv_folds"])
        rows.append({"label": label, "params": params, "roc_auc": round(m["roc_auc"], 4),
                     "pr_auc": round(m["pr_auc"], 4), "seconds": round(time.time() - t0)})
        print(rows[-1], flush=True)

    for cw in t["class_weight_options"]:
        trial({"class_weight": cw}, f"class_weight={cw}")
    for i, p in enumerate(ParameterSampler(t["space"], n_iter=t["n_trials"], random_state=seed)):
        trial(p, f"trial{i}")
    best = max(rows[len(t["class_weight_options"]):], key=lambda r: r["roc_auc"])
    out = {"model": name, "seed": seed, "results": rows, "best_random_search": best}
    Path(cfg["models_dir"], "tuning_results.json").write_text(json.dumps(out, indent=2, default=str))
    print(pd.DataFrame(rows)[["label", "roc_auc", "pr_auc", "seconds"]].to_string(index=False))


if __name__ == "__main__":
    main()
