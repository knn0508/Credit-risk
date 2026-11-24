"""Eyni protokolla CV: OOF proqnozlar + roc_auc/pr_auc. Yalnız train hissəsi verilir (holdout daxil deyil)."""
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import average_precision_score, roc_auc_score

from .protocol import cv_folds


def run_cv(estimator, X: pd.DataFrame, y, ids, seed: int, n_splits: int):
    y = np.asarray(y)
    if len(set(ids)) != len(ids):
        raise ValueError("sk_id_curr unikal olmalıdır")
    oof = pd.DataFrame({"sk_id_curr": np.asarray(ids), "fold": -1, "p_raw": np.nan, "target": y})
    per_fold = []
    for k, a, b in cv_folds(y, seed, n_splits):
        m = clone(estimator).fit(X.iloc[a], y[a])
        p = m.predict_proba(X.iloc[b])[:, 1]
        oof.iloc[b, oof.columns.get_loc("fold")] = k
        oof.iloc[b, oof.columns.get_loc("p_raw")] = p
        per_fold.append({"fold": k, "roc_auc": roc_auc_score(y[b], p), "pr_auc": average_precision_score(y[b], p)})
    oof["fold"] = oof["fold"].astype(int)
    metrics = {"roc_auc": roc_auc_score(y, oof.p_raw), "pr_auc": average_precision_score(y, oof.p_raw)}
    return oof, metrics, per_fold
