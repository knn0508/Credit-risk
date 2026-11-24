import numpy as np
import pandas as pd

from src.models import baselines, bundle, cv, protocol


def _data(n=600, seed=0):
    r = np.random.default_rng(seed)
    X = pd.DataFrame(r.normal(size=(n, 4)), columns=list("abcd"))
    X.iloc[::17, 0] = np.nan
    y = (X.fillna(0).a + r.normal(size=n) > 1.2).astype(int).to_numpy()
    return X, y, np.arange(1000, 1000 + n)


def test_split_deterministic_disjoint():
    X, y, ids = _data()
    s1, s2 = protocol.make_split(ids, y, 42), protocol.make_split(ids, y, 42)
    assert s1 == s2
    assert not set(s1["train_ids"]) & set(s1["holdout_ids"])
    assert len(s1["train_ids"]) + len(s1["holdout_ids"]) == len(ids)


def test_cv_reproducible_and_beats_dummy():
    X, y, ids = _data()
    o1, m1, _ = cv.run_cv(baselines.logreg(), X, y, ids, 42, 5)
    o2, m2, _ = cv.run_cv(baselines.logreg(), X, y, ids, 42, 5)
    assert o1.fold.dtype.kind == "i" and m1 == m2 and (o1.fold >= 0).all() and o1.p_raw.notna().all()
    _, md, _ = cv.run_cv(baselines.dummy(), X, y, ids, 42, 5)
    assert m1["roc_auc"] > md["roc_auc"]


def test_bundle_round_trip_feature_order(tmp_path):
    X, y, ids = _data()
    oof, m, _ = cv.run_cv(baselines.logreg(), X, y, ids, 42, 5)
    model = baselines.logreg().fit(X, y)
    d = bundle.save_bundle(tmp_path, model, list(X.columns), oof, protocol.make_split(ids, y, 42),
                           algorithm="logreg", seed=42, config_path="configs/training.yaml",
                           data_version="x", metrics=m, positive_rate=float(y.mean()))
    model2, names, meta = bundle.load_bundle(d)
    assert names == list(X.columns) and meta["validation_status"] == "unvalidated"
    np.testing.assert_allclose(model2.predict_proba(X[names])[:, 1], model.predict_proba(X)[:, 1])


def test_train_baseline_with_categoricals_and_excluded(tmp_path):
    from src.models import train_baseline as tb
    X, y, ids = _data(800)
    df = X.assign(sk_id_curr=ids, target=y, code_gender=np.where(y == 1, "F", "M"),
                  occ=np.where(np.arange(800) % 3 == 0, "x", "y"))
    df.loc[::50, "occ"] = None
    df.to_parquet(tmp_path / "t.parquet")
    cfg = {"train_data": str(tmp_path / "t.parquet"), "id_col": "sk_id_curr", "target_col": "target",
           "excluded_protected_features": ["code_gender"]}
    Xf, yf, idf = tb.load_xy(cfg)
    assert "code_gender" not in Xf and "sk_id_curr" not in Xf and "target" not in Xf
    _, m, _ = cv.run_cv(tb.logreg_for(Xf, 42), Xf, yf, idf, 42, 5)
    assert m["roc_auc"] > 0.6
