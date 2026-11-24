import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.explainability.shap_explainer import ShapExplainer


def _setup(clf):
    rng = np.random.default_rng(0)
    n = 1500
    X = pd.DataFrame({"a": rng.normal(size=n), "b": rng.normal(size=n),
                      "cat": rng.choice(["x", "y", "z"], n)})
    y = (rng.random(n) < 1 / (1 + np.exp(-(1.5 * X.a - X.b + (X.cat == "x") - 1)))).astype(int)
    pre = ColumnTransformer([("num", StandardScaler(), ["a", "b"]), ("cat", OneHotEncoder(), ["cat"])])
    pipe = Pipeline([("pre", pre), ("clf", clf)]).fit(X, y)
    return pipe, X


@pytest.mark.parametrize("clf", [LogisticRegression(), GradientBoostingClassifier(n_estimators=30, random_state=0)])
def test_additivity_shape_and_order(clf):
    pipe, X = _setup(clf)
    ex = ShapExplainer(pipeline=pipe, background=X)
    sv = ex.shap_values(X.iloc[:50])
    assert sv.shape == (50, 3) and list(sv.columns) == ["a", "b", "cat"]  # one-hot aggregated
    raw = pipe.decision_function(X.iloc[:50])
    assert np.allclose(sv.sum(axis=1) + ex.base_value, raw, atol=1e-3)
    e = ex.explain_row(X.iloc[[0]], top_n=2)
    pos = [f["contribution"] for f in e["top_positive_factors"]]
    neg = [f["contribution"] for f in e["top_negative_factors"]]
    assert pos == sorted(pos, reverse=True) and all(c > 0 for c in pos)
    assert neg == sorted(neg) and all(c < 0 for c in neg)
    assert e["explanation_space"] == "log_odds" and "səbəb-nəticə" in e["note"]


def test_values_only_when_requested():
    pipe, X = _setup(LogisticRegression())
    ex = ShapExplainer(pipe, X)
    r = X.iloc[[0]]
    assert all("value" not in f for f in ex.explain_row(r)["top_positive_factors"])
    e = ex.explain_row(r, include_values=True)
    assert all("value" in f for f in e["top_positive_factors"] + e["top_negative_factors"])
    with pytest.raises(ValueError):
        ex.explain_row(X.iloc[:2])
