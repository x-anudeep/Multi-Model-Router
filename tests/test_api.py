from fastapi.testclient import TestClient

from llm_gateway.api.app import app


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_completion_endpoint() -> None:
    response = TestClient(app).post(
        "/v1/chat/completions",
        json={"prompt": "Summarize this API", "task_type": "summarization"},
    )

    assert response.status_code == 200
    assert response.json()["task_type"] == "summarization"

