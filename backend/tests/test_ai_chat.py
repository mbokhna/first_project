import os

import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.skipif(
    not os.environ.get("OPENROUTER_API_KEY"),
    reason="OPENROUTER_API_KEY not set; skipping live AI chat test",
)


def _login(client: TestClient) -> None:
    response = client.post(
        "/api/login", json={"username": "user", "password": "password"}
    )
    assert response.status_code == 200


def test_plain_question_does_not_change_the_board(client: TestClient):
    _login(client)
    before = client.get("/api/board").json()

    response = client.post(
        "/api/ai/chat", json={"message": "Hi there, how are you?", "history": []}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["reply"]
    assert data["board"] == before


def test_add_card_request_mutates_the_board(client: TestClient):
    _login(client)
    board = client.get("/api/board").json()
    backlog_id = board["columns"][0]["id"]

    response = client.post(
        "/api/ai/chat",
        json={
            "message": (
                f"Please add a card titled 'AI created this' to the column "
                f"with id {backlog_id}."
            ),
            "history": [],
        },
    )
    assert response.status_code == 200
    data = response.json()

    titles = [card["title"] for card in data["board"]["cards"].values()]
    assert "AI created this" in titles
