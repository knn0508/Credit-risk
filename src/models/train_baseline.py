"""Baseline CV + bundle: python -m src.models.train_baseline --model logreg
Giriş: data/processed/application_train.parquet (02/03). Holdout bu skriptdə istifadə olunmur."""
import argparse

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from . import baselines, bundle, cv, protocol


def add_ft(df: pd.DataFrame) -> pd.DataFrame:
    """03-ün stateless ft_ feature-ları (train/inference eyni kod). Index saxlanır."""
    from src.features import AggregateFeatures, ApplicationFeatures
    ft = pd.concat([ApplicationFeatures().fit(df).transform(df), AggregateFeatures().fit(df).transform(df)], axis=1)
    return pd.concat([df, ft], axis=1)


def load_xy(cfg: dict, use_ft: bool | None = None):
    df = pd.read_parquet(cfg["train_data"])
    df.columns = [c.lower() for c in df.columns]
    if cfg.get("use_ft") if use_ft is None else use_ft:
        df = add_ft(df)
    ids, y = df[cfg["id_col"]], df[cfg["target_col"]]
    drop = {cfg["id_col"], cfg["target_col"], *cfg["excluded_protected_features"]}
    pref = tuple(cfg.get("excluded_drift_prefixes") or ())
    cols = [c for c in df.columns if c in drop or (pref and c.startswith(pref))]
    return df.drop(columns=cols), y, ids


def excluded_drift_features(cfg: dict) -> list:
    """Metadata üçün: faktiki xaric edilən drift sütunları (decisions/0003)."""
    pref = tuple(cfg.get("excluded_drift_prefixes") or ())
    cols = pd.read_parquet(cfg["train_data"]).columns
    return sorted(c.lower() for c in cols if pref and c.lower().startswith(pref))


def logreg_for(X: pd.DataFrame, seed: int, class_weight=None):
    """Kateqorial sütunlar varsa one-hot; hamısı Pipeline daxilində (fit yalnız train fold)."""
    cat = X.select_dtypes(exclude="number").columns.tolist()
    num = [c for c in X.columns if c not in cat]
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore", min_frequency=50))]), cat),
    ])
    return Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=2000, class_weight=class_weight,
                                                               random_state=seed))])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["dummy", "logreg"], default="logreg")
    ap.add_argument("--config", default=protocol.DEFAULT_CONFIG)
    a = ap.parse_args()
    cfg = protocol.load_config(a.config)
    seed = cfg["random_seed"]
    X, y, ids = load_xy(cfg)
    split = protocol.make_split(ids, y, seed, cfg["holdout_size"])
    tr = ids.isin(set(split["train_ids"])).to_numpy()
    Xt, yt, it = X[tr].reset_index(drop=True), y[tr].reset_index(drop=True), ids[tr].reset_index(drop=True)
    est = baselines.dummy(seed) if a.model == "dummy" else logreg_for(Xt, seed)
    oof, metrics, per_fold = cv.run_cv(est, Xt, yt, it, seed, cfg["cv_folds"])
    print(pd.DataFrame(per_fold).round(4).to_string(index=False))
    print("OOF:", {k: round(v, 4) for k, v in metrics.items()})
    model = est.fit(Xt, yt)
    d = bundle.save_bundle(cfg["models_dir"], model, list(Xt.columns), oof, split, algorithm=a.model, seed=seed,
                           config_path=a.config, data_version=bundle.data_version(),
                           metrics=metrics, positive_rate=float(yt.mean()), X_train=Xt,
                           excluded_protected_features=cfg["excluded_protected_features"],
                           excluded_drift_features=excluded_drift_features(cfg))
    print("bundle:", d)


if __name__ == "__main__":
    main()
