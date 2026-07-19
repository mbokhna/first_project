import os
import sqlite3
from collections.abc import Generator
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from starlette.middleware.sessions import SessionMiddleware

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

from app import ai, board, db  # noqa: E402

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
SESSION_SECRET = os.environ.get("SESSION_SECRET", "dev-secret-change-me")
DEMO_USERNAME = "user"
DEMO_PASSWORD = "password"

app = FastAPI(title="Project Management App")

app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def _init_app_db() -> None:
    conn = db.get_connection()
    try:
        db.init_db(conn)
    finally:
        conn.close()


_init_app_db()


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


class LoginRequest(BaseModel):
    username: str
    password: str


class RenameColumnRequest(BaseModel):
    title: str


class AddCardRequest(BaseModel):
    column_id: str
    title: str
    details: str = ""


class UpdateCardRequest(BaseModel):
    title: str | None = None
    details: str | None = None


class MoveCardRequest(BaseModel):
    column_id: str
    index: int


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/login")
def login(credentials: LoginRequest, request: Request) -> dict[str, bool]:
    if credentials.username != DEMO_USERNAME or credentials.password != DEMO_PASSWORD:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    request.session["user"] = credentials.username
    return {"ok": True}


@app.post("/api/logout")
def logout(request: Request) -> dict[str, bool]:
    request.session.clear()
    return {"ok": True}


@app.get("/api/session")
def session(request: Request) -> dict[str, bool]:
    return {"authenticated": "user" in request.session}


@app.get("/api/board")
def get_board(
    username: str = Depends(require_user), conn: sqlite3.Connection = Depends(get_db)
) -> dict[str, Any]:
    try:
        return board.get_board(conn, username)
    except board.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.patch("/api/board/columns/{column_id}")
def rename_column(
    column_id: str,
    body: RenameColumnRequest,
    username: str = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    try:
        board.rename_column(conn, column_id, body.title)
        return board.get_board(conn, username)
    except board.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.post("/api/board/cards")
def add_card(
    body: AddCardRequest,
    username: str = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    try:
        board.add_card(conn, body.column_id, body.title, body.details)
        return board.get_board(conn, username)
    except board.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.patch("/api/board/cards/{card_id}")
def update_card(
    card_id: str,
    body: UpdateCardRequest,
    username: str = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    try:
        board.update_card(conn, card_id, body.title, body.details)
        return board.get_board(conn, username)
    except board.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.delete("/api/board/cards/{card_id}")
def delete_card(
    card_id: str,
    username: str = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    try:
        board.delete_card(conn, card_id)
        return board.get_board(conn, username)
    except board.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.post("/api/board/cards/{card_id}/move")
def move_card(
    card_id: str,
    body: MoveCardRequest,
    username: str = Depends(require_user),
    conn: sqlite3.Connection = Depends(get_db),
) -> dict[str, Any]:
    try:
        board.move_card(conn, card_id, body.column_id, body.index)
        return board.get_board(conn, username)
    except board.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error))


@app.get("/api/ai/ping")
def ai_ping(username: str = Depends(require_user)) -> dict[str, str]:
    try:
        reply = ai.ask("What is 2+2? Reply with only the number, no words.")
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error))
    return {"reply": reply}


app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
