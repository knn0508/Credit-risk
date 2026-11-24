"""SHAP explanations for Pipeline(pre=ColumnTransformer, clf) bundles (contract: docs/contracts/explanation.md).

SHAP describes model behaviour, not causal evidence. Space: log-odds of the RAW model (before calibration).
One-hot SHAP values are summed back to the original input feature. Never log individual explanations.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import shap

NOTE = "SHAP model davranışını izah edir, səbəb-nəticə sübutu deyil."


def _source_map(out_names, input_cols):
    """transformed column name -> original input column (longest-prefix match after stripping 'num__'/'cat__')."""
    cols = sorted(input_cols, key=len, reverse=True)
    res = []
    for n in out_names:
        s = n.split("__", 1)[-1]
        src = next((c for c in cols if s == c or s.startswith(c + "_")), None)
        if src is None:
            raise ValueError(f"cannot map transformed feature {n!r} to an input feature")
        res.append(src)
    return np.array(res)


class ShapExplainer:
    def __init__(self, pipeline, background: pd.DataFrame, display_names: dict | None = None,
                 max_background: int = 1000, seed: int = 42):
        self.pre, self.clf = pipeline.named_steps["pre"], pipeline.named_steps["clf"]
        self.input_cols = list(background.columns)
        self.display = display_names or {}
        names = self.pre.get_feature_names_out()
        self.src = _source_map(names, self.input_cols)
        bg = background.sample(min(max_background, len(background)), random_state=seed)
        Xb = self._transform(bg)
        if hasattr(self.clf, "coef_"):
            self.method, self._ex = "shap_linear", shap.LinearExplainer(self.clf, Xb)
        else:
            self.method, self._ex = "shap_tree", shap.TreeExplainer(self.clf)

    def _transform(self, X):
        Xt = self.pre.transform(X[self.input_cols])
        return Xt.toarray() if hasattr(Xt, "toarray") else np.asarray(Xt)

    @property
    def base_value(self) -> float:
        b = np.ravel(self._ex.expected_value)
        return float(b[-1])

    def shap_values(self, X: pd.DataFrame) -> pd.DataFrame:
        """(n_rows, n_input_features) SHAP in log-odds, aggregated to original features."""
        sv = self._ex.shap_values(self._transform(X))
        if isinstance(sv, list):
            sv = sv[-1]
        sv = np.asarray(sv)
        if sv.ndim == 3:
            sv = sv[..., -1]
        df = pd.DataFrame(sv).T.groupby(self.src).sum().T
        df.index = X.index
        return df[self.input_cols]

    def explain_row(self, row: pd.DataFrame, top_n: int = 5, include_values: bool = False) -> dict:
        if len(row) != 1:
            raise ValueError("explain_row expects a single-row DataFrame")
        sv = self.shap_values(row).iloc[0]

        def item(f):
            d = {"feature_name": f, "display_name": self.display.get(f, f), "contribution": float(sv[f])}
            if include_values:
                v = row.iloc[0][f]
                d["value"] = None if pd.isna(v) else (v.item() if hasattr(v, "item") else v)
            return d

        pos = sv[sv > 0].sort_values(ascending=False).index[:top_n]
        neg = sv[sv < 0].sort_values().index[:top_n]
        return {"method": self.method, "explanation_space": "log_odds", "base_value": self.base_value,
                "top_positive_factors": [item(f) for f in pos],
                "top_negative_factors": [item(f) for f in neg], "note": NOTE}

    def global_importance(self, X: pd.DataFrame) -> pd.Series:
        return self.shap_values(X).abs().mean().sort_values(ascending=False)
