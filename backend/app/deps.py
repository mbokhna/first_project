import sqlite3
from collections.abc import Generator

from fastapi import HTTPException, Request

from app import db


def get_db() -> Generator[sqlite3.Connection, None, None]:
    conn = db.get_connection()
    try:
        yield conn
    finally:
        conn.close()


def require_user(request: Request) -> str:
    username = request.session.get("user")
    if not username:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return username
