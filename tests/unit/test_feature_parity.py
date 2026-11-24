"""Train/inference paritet: fit train-də, tək sətir transform == batch nəticəsi (joblib round-trip daxil)."""
import io

import joblib
import numpy as np
import pandas as pd
import pytest

from src.features import AggregateFeatures, ApplicationFeatures, Winsorizer

PATH = "data/processed/application_train.parquet"


@pytest.fixture(scope="module")
def data():
    try:
        d = pd.read_parquet(PATH).set_index("sk_id_curr")
    except FileNotFoundError:
        pytest.skip("processed data yoxdur")
    d = d.sample(2000, random_state=42)
    return d.drop(columns="target")


def build(d):
    return pd.concat([ApplicationFeatures().fit(d).transform(d), AggregateFeatures().fit(d).transform(d)], axis=1)


def roundtrip(obj):
    b = io.BytesIO(); joblib.dump(obj, b); b.seek(0); return joblib.load(b)


@pytest.mark.parametrize("cls", [ApplicationFeatures, AggregateFeatures])
def test_single_row_equals_batch(data, cls):
    t = roundtrip(cls().fit(data))
    batch = t.transform(data)
    for i in (0, 7, 1999):
        row = t.transform(data.iloc[[i]])
        pd.testing.assert_frame_equal(row, batch.iloc[[i]], check_exact=True)


def test_winsorizer_fit_train_only_and_parity(data):
    train, test = data.iloc[:1500], data.iloc[1500:]
    w = Winsorizer(columns=["amt_income_total"]).fit(train)
    lo, hi = w.bounds_["amt_income_total"]
    assert lo == train.amt_income_total.quantile(.01) and hi == train.amt_income_total.quantile(.99)
    w2 = roundtrip(w)
    batch = w2.transform(test)
    row = w2.transform(test.iloc[[3]])
    assert row["amt_income_total"].iloc[0] == batch["amt_income_total"].iloc[3]
    assert batch["amt_income_total"].max() <= hi          # test-dən sərhəd ÖYRƏNİLMƏYİB
    assert test.amt_income_total.max() >= batch["amt_income_total"].max()


def test_winsorizer_keeps_nan_and_missing_columns():
    d = pd.DataFrame({"amt_income_total": [1.0, 2.0, np.nan, 1000.0]})
    out = Winsorizer(lower=0, upper=.5).fit(d).transform(d)
    assert out.amt_income_total.isna().tolist() == [False, False, True, False]
    assert out.amt_income_total.max() == 2.0


def test_input_not_mutated(data):
    before = data.copy()
    Winsorizer().fit(data).transform(data)
    ApplicationFeatures().transform(data)
    pd.testing.assert_frame_equal(before, data)
