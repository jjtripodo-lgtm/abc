import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from app import app  # noqa: E402


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)
