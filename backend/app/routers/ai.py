import sqlite3
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app import ai as ai_client
from app import board as board_repo
from app.deps import get_db, require_user
from app.schemas import ChatRequest

router = APIRouter(tags=["ai"])

Username = Annotated[str, Depends(require_user)]
Connection = Annotated[sqlite3.Connection, Depends(get_db)]


@router.get("/api/ai/ping")
def ai_ping(username: Username) -> dict[str, str]:
    try:
        reply = ai_client.ask("What is 2+2? Reply with only the number, no words.")
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"reply": reply}


@router.post("/api/ai/chat")
def ai_chat(body: ChatRequest, username: Username, conn: Connection) -> dict[str, Any]:
    current_board = board_repo.get_board(conn, username)
    history = [{"role": m.role, "content": m.content} for m in body.history]

    try:
        result = ai_client.chat(current_board, history, body.message)
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    for action in result.actions:
        try:
            board_repo.apply_ai_action(conn, action.model_dump(exclude_none=True))
        except (board_repo.NotFoundError, KeyError):
            continue

    return {"reply": result.reply, "board": board_repo.get_board(conn, username)}
