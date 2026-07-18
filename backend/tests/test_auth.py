from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_session_starts_unauthenticated():
    response = client.get("/api/session")
    assert response.json() == {"authenticated": False}


def test_login_rejects_wrong_credentials():
    response = client.post(
        "/api/login", json={"username": "user", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_then_session_then_logout():
    session = TestClient(app)

    login_response = session.post(
        "/api/login", json={"username": "user", "password": "password"}
    )
    assert login_response.status_code == 200
    assert login_response.json() == {"ok": True}

    session_response = session.get("/api/session")
    assert session_response.json() == {"authenticated": True}

    logout_response = session.post("/api/logout")
    assert logout_response.status_code == 200

    session_after_logout = session.get("/api/session")
    assert session_after_logout.json() == {"authenticated": False}
