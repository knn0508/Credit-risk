"""Benchmark: RF / LightGBM / XGBoost / CatBoost, eyni protokol (protocol.py + cv.py). Resampling YOXDUR.
Kateqorial → OrdinalEncoder (Pipeline daxilində, fit yalnız train fold). python -m src.models.benchmark --models lgbm xgb"""
import argparse
import json
import time
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from . import bundle, cv, protocol
from .train_baseline import load_xy


def _wrap(X: pd.DataFrame, clf):
    cat = X.select_dtypes(exclude="number").columns.tolist()
    enc = OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1, encoded_missing_value=-1)
    pre = ColumnTransformer([("cat", enc, cat)], remainder="passthrough", verbose_feature_names_out=False)
    pre.set_output(transform="pandas")
    return Pipeline([("pre", pre), ("clf", clf)])


def make(name: str, X: pd.DataFrame, seed: int, params: dict | None = None):
    p = (params or {})
    if name == "rf":
        clf = RandomForestClassifier(**{"n_estimators": 300, "min_samples_leaf": 50, "max_features": "sqrt",
                                        "n_jobs": -1, "random_state": seed, **p})
    elif name == "lgbm":
        from lightgbm import LGBMClassifier
        clf = LGBMClassifier(**{"n_estimators": 600, "learning_rate": 0.03, "num_leaves": 31,
                                "colsample_bytree": 0.5, "subsample": 0.8, "subsample_freq": 1,
                                "min_child_samples": 100, "random_state": seed, "verbose": -1, **p})
    elif name == "xgb":
        from xgboost import XGBClassifier
        clf = XGBClassifier(**{"n_estimators": 600, "learning_rate": 0.03, "max_depth": 5,
                               "colsample_bytree": 0.5, "subsample": 0.8, "min_child_weight": 20,
                               "tree_method": "hist", "random_state": seed, "n_jobs": -1, **p})
    elif name == "catboost":
        from catboost import CatBoostClassifier
        clf = CatBoostClassifier(**{"iterations": 800, "learning_rate": 0.05, "depth": 6,
                                    "random_seed": seed, "verbose": 0, "thread_count": -1, "allow_writing_files": False, **p})
    else:
        raise ValueError(name)
    return _wrap(X, clf)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--models", nargs="+", default=["lgbm", "xgb", "catboost", "rf"])
    ap.add_argument("--config", default=protocol.DEFAULT_CONFIG)
    ap.add_argument("--save", action="store_true", help="hər model üçün bundle yaz")
    a = ap.parse_args()
    cfg = protocol.load_config(a.config)
    seed = cfg["random_seed"]
    X, y, ids = load_xy(cfg)
    split = protocol.make_split(ids, y, seed, cfg["holdout_size"])
    tr = ids.isin(set(split["train_ids"])).to_numpy()
    Xt, yt, it = X[tr].reset_index(drop=True), y[tr].reset_index(drop=True), ids[tr].reset_index(drop=True)
    rows = []
    for name in a.models:
        t0 = time.time()
        est = make(name, Xt, seed, (cfg.get("model_params") or {}).get(name))
        oof, m, pf = cv.run_cv(est, Xt, yt, it, seed, cfg["cv_folds"])
        m = {**m, "seconds": round(time.time() - t0)}
        rows.append({"model": name, **{k: round(v, 4) for k, v in m.items()},
                     "fold_auc_std": round(pd.DataFrame(pf).roc_auc.std(), 4)})
        print(rows[-1], flush=True)
        if a.save:
            model = est.fit(Xt, yt)
            bundle.save_bundle(cfg["models_dir"], model, list(Xt.columns), oof, split, algorithm=name, seed=seed,
                               config_path=a.config, data_version=bundle.data_version(),
                               metrics={k: m[k] for k in ("roc_auc", "pr_auc")}, positive_rate=float(yt.mean()),
                               excluded_protected_features=cfg["excluded_protected_features"])
    out = Path(cfg["models_dir"]) / "benchmark_results.json"
    out.write_text(json.dumps(rows, indent=2))
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
