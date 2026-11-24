import pytest
from fastapi.testclient import TestClient

from api.bundle import load_bundle
from api.main import create_app
from tests.mock.make_bundle import install_band_stub, make_bundle

install_band_stub()


@pytest.fixture
def bundle_dir(tmp_path):
    return make_bundle(tmp_path / "b")


@pytest.fixture
def client(bundle_dir):
    return TestClient(create_app(load_bundle(bundle_dir, allow_dev=True)))
