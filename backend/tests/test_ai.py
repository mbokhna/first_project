import os

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set; skipping live AI connectivity test",
)


def _login(client: TestClient) -> None:
    response = client.post(
        "/api/login", json={"username": "user", "password": "password"}
    )
    assert response.status_code == 200


def test_ai_ping_answers_2_plus_2(client: TestClient):
    _login(client)
    response = client.get("/api/ai/ping")
    assert response.status_code == 200
    assert "4" in response.json()["reply"]
