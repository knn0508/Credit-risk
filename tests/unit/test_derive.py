import math

import pytest

from api import service
from api.bundle import Bundle

NAMES = ["amt_credit", "amt_income_total", "ext_source_1", "ext_source_2", "ext_source_3",
         "ft_credit_income_ratio", "ft_ext_source_mean", "ft_ext_source_missing_cnt"]


def bundle():
    return Bundle(model=None, calibrator=None, feature_names=NAMES, metadata={}, risk_policy={}, dev_mode=True)


def test_ft_computed_by_shared_feature_code():
    X, w = service.to_frame(bundle(), [{"amt_credit": 600.0, "amt_income_total": 200.0,
                                         "ext_source_1": 0.2, "ext_source_2": 0.4}])
    r = X.iloc[0]
    assert r["ft_credit_income_ratio"] == pytest.approx(3.0)
    assert r["ft_ext_source_mean"] == pytest.approx(0.3) and r["ft_ext_source_missing_cnt"] == 1
    assert any("törəmə" in x for x in w[0]) and not any("ft_" in x and "çatışmayan" in x for x in w[0])


def test_supplied_ft_wins_and_missing_inputs_give_nan():
    X, _ = service.to_frame(bundle(), [{"amt_credit": 600.0, "amt_income_total": 200.0, "ft_credit_income_ratio": 9.0},
                                       {"amt_credit": 600.0}])
    assert X.iloc[0]["ft_credit_income_ratio"] == 9.0
    assert math.isnan(X.iloc[1]["ft_credit_income_ratio"])


def test_non_numeric_input_for_derivation_raises():
    with pytest.raises(ValueError):
        service.to_frame(bundle(), [{"amt_credit": "abc", "amt_income_total": 1.0}])
