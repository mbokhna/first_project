import sqlite3
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app import board as board_repo
from app.deps import get_db, require_user
from app.schemas import (
    AddCardRequest,
    MoveCardRequest,
    RenameColumnRequest,
    UpdateCardRequest,
)

router = APIRouter(tags=["board"])

Username = Annotated[str, Depends(require_user)]
Connection = Annotated[sqlite3.Connection, Depends(get_db)]


@router.get("/api/board")
def get_board(username: Username, conn: Connection) -> dict[str, Any]:
    try:
        return board_repo.get_board(conn, username)
    except board_repo.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/api/board/columns/{column_id}")
def rename_column(
    column_id: str,
    body: RenameColumnRequest,
    username: Username,
    conn: Connection,
) -> dict[str, Any]:
    try:
        board_repo.rename_column(conn, column_id, body.title)
        return board_repo.get_board(conn, username)
    except board_repo.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/api/board/cards")
def add_card(
    body: AddCardRequest, username: Username, conn: Connection
) -> dict[str, Any]:
    try:
        board_repo.add_card(conn, body.column_id, body.title, body.details)
        return board_repo.get_board(conn, username)
    except board_repo.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.patch("/api/board/cards/{card_id}")
def update_card(
    card_id: str,
    body: UpdateCardRequest,
    username: Username,
    conn: Connection,
) -> dict[str, Any]:
    try:
        board_repo.update_card(conn, card_id, body.title, body.details)
        return board_repo.get_board(conn, username)
    except board_repo.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.delete("/api/board/cards/{card_id}")
def delete_card(card_id: str, username: Username, conn: Connection) -> dict[str, Any]:
    try:
        board_repo.delete_card(conn, card_id)
        return board_repo.get_board(conn, username)
    except board_repo.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@router.post("/api/board/cards/{card_id}/move")
def move_card(
    card_id: str,
    body: MoveCardRequest,
    username: Username,
    conn: Connection,
) -> dict[str, Any]:
    try:
        board_repo.move_card(conn, card_id, body.column_id, body.index)
        return board_repo.get_board(conn, username)
    except board_repo.NotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
