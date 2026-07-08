import pytest

pytest.importorskip("fastapi")
pytest.importorskip("pydantic")
pytest.importorskip("pydantic_settings")

from fastapi.testclient import TestClient

from app.api import dependencies
from app.main import app


def reset_app_state() -> None:
    dependencies.container = dependencies.create_container()


def test_api_mock_comment_to_avatar_speech_flow() -> None:
    reset_app_state()
    client = TestClient(app)

    product = client.post("/api/v1/products", json={"title": "保湿面霜"}).json()["data"]
    product_id = product["id"]
    client.post(
        f"/api/v1/products/{product_id}/skus",
        json={"name": "50ml", "price_cents": 12900, "stock": 88},
    )
    client.post(
        f"/api/v1/products/{product_id}/faqs",
        json={"question": "这款多少钱", "answer": "今天以页面价格为准"},
    )
    client.post(f"/api/v1/products/{product_id}/selling-points", json={"text": "温和保湿"})
    client.post(f"/api/v1/products/{product_id}/index")

    session = client.post("/api/v1/live-sessions", json={"product_id": product_id}).json()["data"]
    session_id = session["id"]
    client.post(f"/api/v1/live-sessions/{session_id}/start")

    comment_response = client.post(
        f"/api/v1/live-sessions/{session_id}/mock-comments",
        json={"content": "这款多少钱？", "user": "观众A"},
    ).json()["data"]
    review_id = comment_response["review"]["id"]
    candidate = comment_response["candidate"]
    assert candidate["risk"] == "low"

    approve_response = client.post(
        f"/api/v1/review-tasks/{review_id}/approve",
        json={"reviewer_id": "operator-1"},
    ).json()["data"]
    speech_id = approve_response["speech_task"]["id"]

    played = client.post(f"/api/v1/speech-tasks/{speech_id}/play").json()["data"]
    assert played["status"] == "finished"

    speeches = client.get("/api/v1/speech-tasks").json()["data"]
    assert speeches[0]["status"] == "finished"


def test_api_blocks_blocked_candidate_before_speech_task_creation() -> None:
    reset_app_state()
    client = TestClient(app)

    product = client.post("/api/v1/products", json={"title": "修护霜"}).json()["data"]
    product_id = product["id"]
    client.post(
        f"/api/v1/products/{product_id}/skus",
        json={"name": "默认", "price_cents": 9900, "stock": 20},
    )
    session = client.post("/api/v1/live-sessions", json={"product_id": product_id}).json()["data"]
    session_id = session["id"]
    client.post(f"/api/v1/live-sessions/{session_id}/start")

    comment_response = client.post(
        f"/api/v1/live-sessions/{session_id}/mock-comments",
        json={"content": "能治好湿疹吗？", "user": "观众B"},
    ).json()["data"]
    review_id = comment_response["review"]["id"]

    services = dependencies.get_container()
    candidate_id = comment_response["candidate"]["id"]
    candidate = services.store.candidates[candidate_id]
    candidate.text = "这款能治好湿疹"
    services.compliance.check(candidate, product=services.store.products[product_id])

    blocked = client.post(
        f"/api/v1/review-tasks/{review_id}/approve",
        json={"reviewer_id": "operator-1"},
    )
    assert blocked.status_code == 400
    assert client.get("/api/v1/speech-tasks").json()["data"] == []
