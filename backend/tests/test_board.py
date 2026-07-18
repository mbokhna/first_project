from fastapi.testclient import TestClient


def _login(client: TestClient) -> None:
    response = client.post(
        "/api/login", json={"username": "user", "password": "password"}
    )
    assert response.status_code == 200


def test_get_board_requires_auth(client: TestClient):
    response = client.get("/api/board")
    assert response.status_code == 401


def test_get_board_returns_seeded_columns(client: TestClient):
    _login(client)
    response = client.get("/api/board")
    assert response.status_code == 200
    data = response.json()
    assert [c["title"] for c in data["columns"]] == [
        "Backlog",
        "Discovery",
        "In Progress",
        "Review",
        "Done",
    ]
    assert data["cards"] == {}


def test_rename_column(client: TestClient):
    _login(client)
    board = client.get("/api/board").json()
    column_id = board["columns"][0]["id"]

    response = client.patch(
        f"/api/board/columns/{column_id}", json={"title": "Ideas"}
    )
    assert response.status_code == 200
    assert response.json()["columns"][0]["title"] == "Ideas"


def test_rename_missing_column_is_404(client: TestClient):
    _login(client)
    response = client.patch("/api/board/columns/col-9999", json={"title": "Ideas"})
    assert response.status_code == 404


def test_add_card(client: TestClient):
    _login(client)
    board = client.get("/api/board").json()
    column_id = board["columns"][0]["id"]

    response = client.post(
        "/api/board/cards",
        json={"column_id": column_id, "title": "New task", "details": "notes"},
    )
    assert response.status_code == 200
    data = response.json()
    card_id = data["columns"][0]["cardIds"][0]
    assert data["cards"][card_id] == {
        "id": card_id,
        "title": "New task",
        "details": "notes",
    }


def test_update_and_delete_card(client: TestClient):
    _login(client)
    board = client.get("/api/board").json()
    column_id = board["columns"][0]["id"]
    added = client.post(
        "/api/board/cards",
        json={"column_id": column_id, "title": "Task", "details": ""},
    ).json()
    card_id = added["columns"][0]["cardIds"][0]

    updated = client.patch(
        f"/api/board/cards/{card_id}", json={"title": "Updated"}
    ).json()
    assert updated["cards"][card_id]["title"] == "Updated"
    assert updated["cards"][card_id]["details"] == ""

    deleted = client.delete(f"/api/board/cards/{card_id}").json()
    assert deleted["cards"] == {}
    assert deleted["columns"][0]["cardIds"] == []


def test_move_card_between_columns(client: TestClient):
    _login(client)
    board = client.get("/api/board").json()
    source_column_id = board["columns"][0]["id"]
    target_column_id = board["columns"][1]["id"]

    added = client.post(
        "/api/board/cards",
        json={"column_id": source_column_id, "title": "Task", "details": ""},
    ).json()
    card_id = added["columns"][0]["cardIds"][0]

    moved = client.post(
        f"/api/board/cards/{card_id}/move",
        json={"column_id": target_column_id, "index": 0},
    ).json()

    assert card_id in moved["columns"][1]["cardIds"]
    assert card_id not in moved["columns"][0]["cardIds"]


def test_move_card_reorders_within_same_column(client: TestClient):
    _login(client)
    board = client.get("/api/board").json()
    column_id = board["columns"][0]["id"]

    for title in ["A", "B", "C"]:
        client.post(
            "/api/board/cards",
            json={"column_id": column_id, "title": title, "details": ""},
        )
    board = client.get("/api/board").json()
    card_ids = board["columns"][0]["cardIds"]
    first_card_id = card_ids[0]

    moved = client.post(
        f"/api/board/cards/{first_card_id}/move",
        json={"column_id": column_id, "index": 2},
    ).json()

    assert moved["columns"][0]["cardIds"][-1] == first_card_id
