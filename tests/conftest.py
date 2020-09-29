import pytest

from app.main import app


@pytest.fixture  # default function scope to work with clean db.
def test_client():
    yield app.test_client()
