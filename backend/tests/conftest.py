from pathlib import Path
from typing import Generator

import pytest
from fastapi.testclient import TestClient

from app import db
from app.main import app, get_db


@pytest.fixture
def client(tmp_path: Path) -> Generator[TestClient, None, None]:
    db_path = tmp_path / "test.db"
    init_conn = db.get_connection(db_path)
    db.init_db(init_conn)
    init_conn.close()

    def override_get_db() -> Generator:
        conn = db.get_connection(db_path)
        try:
            yield conn
        finally:
            conn.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
