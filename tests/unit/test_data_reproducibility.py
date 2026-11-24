"""Build reproducibility: two independent builds -> identical data + data_sha256 (slow: ~1.5 min, needs data/raw)."""
import hashlib
import json
from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from src.data.build import build
from src.data.inventory import load_config

RAW = Path("data/raw")
pytestmark = pytest.mark.skipif(not (RAW / "application_train.csv").exists(), reason="data/raw missing")


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def test_two_builds_are_identical(tmp_path):
    cfg = load_config("configs/data.yaml")
    out = []
    for name in ("a", "b"):
        d = tmp_path / name
        build({**cfg, "processed_dir": str(d)})
        out.append(d)
    a, b = out
    for f in ("application_train.parquet", "application_test.parquet"):
        assert_frame_equal(pd.read_parquet(a / f), pd.read_parquet(b / f), check_exact=True)
    sa, sb = (json.loads((d / "schema.json").read_text()) for d in out)
    assert sa["meta"]["data_sha256"] == sb["meta"]["data_sha256"]
    assert sa["meta"]["raw_files"] == sb["meta"]["raw_files"]
    assert sa["columns"] == sb["columns"]
    # the parquet bytes are expected to match too; this guards accidental nondeterminism (e.g. unordered groupby)
    for f in ("application_train.parquet", "application_test.parquet"):
        assert _sha(a / f) == _sha(b / f)


def test_build_matches_committed_data_version():
    p = Path("data/processed/schema.json")
    if not p.exists():
        pytest.skip("data/processed not built")
    cur = json.loads(p.read_text())["meta"]
    from src.data.build import data_version
    assert data_version(RAW)["data_version"] == cur["data_version"], "raw data changed since last build: rebuild"
