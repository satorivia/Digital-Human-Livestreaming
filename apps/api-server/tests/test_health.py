import pytest

pytest.importorskip("pydantic")
pytest.importorskip("fastapi")
pytest.importorskip("pydantic_settings")

from fastapi.testclient import TestClient

from app.main import app


def test_healthz() -> None:
    response = TestClient(app).get("/api/v1/healthz")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "ok"
