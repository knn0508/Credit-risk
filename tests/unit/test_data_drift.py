"""PSI helpers (Agent 02 -> 05)."""
import numpy as np
import pandas as pd

from src.data.drift import drift_table, psi_categorical, psi_numeric


def test_identical_distributions_have_zero_psi():
    rng = np.random.default_rng(0)
    s = pd.Series(rng.normal(size=5000))
    assert psi_numeric(s, s) < 1e-9
    c = pd.Series(["a", "b", "a", None] * 100)
    assert psi_categorical(c, c) < 1e-9


def test_shift_and_null_pattern_are_detected():
    rng = np.random.default_rng(0)
    a = pd.Series(rng.normal(size=5000))
    assert psi_numeric(a, a + 2) > 0.25
    b = a.copy()
    b[:2500] = np.nan  # same values, different missingness
    assert psi_numeric(a, b) > 0.25


def test_unseen_category_counts_as_drift():
    a = pd.Series(["x"] * 90 + ["y"] * 10)
    assert psi_categorical(a, pd.Series(["x"] * 50 + ["z"] * 50)) > 0.25


def test_drift_table_skips_key_and_target_and_sorts():
    rng = np.random.default_rng(1)
    tr = pd.DataFrame({"sk_id_curr": range(1000), "target": 0, "stable": rng.normal(size=1000),
                       "moved": rng.normal(size=1000), "cat": ["a", "b"] * 500})
    te = tr.assign(moved=tr.moved + 3)
    t = drift_table(tr, te)
    assert list(t.column)[0] == "moved" and not {"sk_id_curr", "target"} & set(t.column)
