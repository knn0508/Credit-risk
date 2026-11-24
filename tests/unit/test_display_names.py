"""UX: hər bundle feature-ı üçün oxunaqlı display_name (explanation.md). Bundle yoxdursa skip."""
import glob
import json

import pytest
import yaml

from src.features import AggregateFeatures, ApplicationFeatures

NAMES = yaml.safe_load(open("configs/feature_display_names.yaml", encoding="utf-8"))


def test_all_ft_features_have_display_names():
    ft = list(ApplicationFeatures().get_feature_names_out()) + list(AggregateFeatures().get_feature_names_out())
    assert [f for f in ft if f not in NAMES] == []


def test_display_names_are_readable():
    bad = [k for k, v in NAMES.items() if not isinstance(v, str) or not v.strip() or v == k or "_" in v]
    assert bad == []


def test_bundle_feature_names_covered():
    files = glob.glob("artifacts/models/*/feature_names.json")
    if not files:
        pytest.skip("model bundle yoxdur")
    missing = {f: sorted(set(json.load(open(f))) - set(NAMES)) for f in files}
    missing = {f: m for f, m in missing.items() if m}
    assert missing == {}
