import numpy as np
import pandas as pd

from src.evaluation.subgroups import age_groups, audit


def test_age_groups_boundaries():
    s = age_groups(pd.Series([-29 * 365.25, -30 * 365.25, -59.9 * 365.25, -60 * 365.25]))
    assert list(s) == ["<30", "30-39", "50-59", "60+"]


def test_audit_unknown_and_insufficient():
    rng = np.random.default_rng(0)
    n = 1000
    p = rng.beta(1, 11, n)
    df = pd.DataFrame({"target": (rng.random(n) < p).astype(int), "p_cal": p,
                       "g": ["F"] * 600 + ["M"] * 396 + [None] * 4})
    a = audit(df, "g", 0.05, 0.15).set_index("group")
    assert set(a.index) == {"F", "M", "unknown"}
    assert a.loc["unknown", "auc"] == "insufficient"
    assert a.n.sum() == n and 0 <= a.high_share.max() <= 1
    assert isinstance(a.loc["F", "auc"], float)


def test_to_md_table():
    from src.evaluation.run_audit import to_md
    t = to_md(pd.DataFrame({"a": [1], "b": ["x"]}))
    assert t.splitlines() == ["| a | b |", "|---|---|", "| 1 | x |"]
