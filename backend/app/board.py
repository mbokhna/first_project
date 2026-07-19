import sqlite3
from typing import Any


class NotFoundError(Exception):
    pass


def _column_id_to_int(column_id: str) -> int:
    if not column_id.startswith("col-"):
        raise NotFoundError(f"Invalid column id: {column_id}")
    return int(column_id.removeprefix("col-"))


def _card_id_to_int(card_id: str) -> int:
    if not card_id.startswith("card-"):
        raise NotFoundError(f"Invalid card id: {card_id}")
    return int(card_id.removeprefix("card-"))


def _get_user_id(conn: sqlite3.Connection, username: str) -> int:
    row = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"No user named {username!r}")
    return row["id"]


def _get_board_id(conn: sqlite3.Connection, user_id: int) -> int:
    row = conn.execute("SELECT id FROM boards WHERE user_id = ?", (user_id,)).fetchone()
    if row is None:
        raise NotFoundError("No board for this user")
    return row["id"]


def _get_column_board_id(conn: sqlite3.Connection, column_id: int) -> int:
    row = conn.execute(
        "SELECT board_id FROM kanban_columns WHERE id = ?", (column_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"No column {column_id}")
    return row["board_id"]


def _get_card_column_id(conn: sqlite3.Connection, card_id: int) -> int:
    row = conn.execute(
        "SELECT column_id FROM cards WHERE id = ?", (card_id,)
    ).fetchone()
    if row is None:
        raise NotFoundError(f"No card {card_id}")
    return row["column_id"]


def _card_ids_in_column(conn: sqlite3.Connection, column_id: int) -> list[int]:
    rows = conn.execute(
        "SELECT id FROM cards WHERE column_id = ? ORDER BY position", (column_id,)
    ).fetchall()
    return [row["id"] for row in rows]


def _renumber_column(
    conn: sqlite3.Connection, column_id: int, card_ids: list[int]
) -> None:
    for position, card_id in enumerate(card_ids):
        conn.execute(
            "UPDATE cards SET column_id = ?, position = ? WHERE id = ?",
            (column_id, position, card_id),
        )


def get_board(conn: sqlite3.Connection, username: str) -> dict[str, Any]:
    user_id = _get_user_id(conn, username)
    board_id = _get_board_id(conn, user_id)

    columns = conn.execute(
        "SELECT id, title FROM kanban_columns WHERE board_id = ? ORDER BY position",
        (board_id,),
    ).fetchall()

    all_cards = conn.execute(
        """
        SELECT cards.id, cards.column_id, cards.title, cards.details
        FROM cards
        JOIN kanban_columns ON kanban_columns.id = cards.column_id
        WHERE kanban_columns.board_id = ?
        ORDER BY cards.position
        """,
        (board_id,),
    ).fetchall()

    card_ids_by_column: dict[int, list[str]] = {c["id"]: [] for c in columns}
    cards: dict[str, Any] = {}
    for card in all_cards:
        card_id = f"card-{card['id']}"
        card_ids_by_column[card["column_id"]].append(card_id)
        cards[card_id] = {
            "id": card_id,
            "title": card["title"],
            "details": card["details"],
        }

    return {
        "columns": [
            {
                "id": f"col-{column['id']}",
                "title": column["title"],
                "cardIds": card_ids_by_column[column["id"]],
            }
            for column in columns
        ],
        "cards": cards,
    }


def rename_column(conn: sqlite3.Connection, column_id: str, title: str) -> None:
    column_id_int = _column_id_to_int(column_id)
    cursor = conn.execute(
        "UPDATE kanban_columns SET title = ? WHERE id = ?", (title, column_id_int)
    )
    if cursor.rowcount == 0:
        raise NotFoundError(f"No column {column_id}")
    conn.commit()


def add_card(conn: sqlite3.Connection, column_id: str, title: str, details: str) -> str:
    column_id_int = _column_id_to_int(column_id)
    _get_column_board_id(conn, column_id_int)

    next_position = len(_card_ids_in_column(conn, column_id_int))
    cursor = conn.execute(
        "INSERT INTO cards (column_id, title, details, position) VALUES (?, ?, ?, ?)",
        (column_id_int, title, details, next_position),
    )
    conn.commit()
    return f"card-{cursor.lastrowid}"


def update_card(
    conn: sqlite3.Connection,
    card_id: str,
    title: str | None,
    details: str | None,
) -> None:
    card_id_int = _card_id_to_int(card_id)
    _get_card_column_id(conn, card_id_int)

    if title is not None:
        conn.execute("UPDATE cards SET title = ? WHERE id = ?", (title, card_id_int))
    if details is not None:
        conn.execute(
            "UPDATE cards SET details = ? WHERE id = ?", (details, card_id_int)
        )
    conn.commit()


def delete_card(conn: sqlite3.Connection, card_id: str) -> None:
    card_id_int = _card_id_to_int(card_id)
    column_id = _get_card_column_id(conn, card_id_int)

    conn.execute("DELETE FROM cards WHERE id = ?", (card_id_int,))
    remaining = _card_ids_in_column(conn, column_id)
    _renumber_column(conn, column_id, remaining)
    conn.commit()


def move_card(
    conn: sqlite3.Connection, card_id: str, target_column_id: str, index: int
) -> None:
    card_id_int = _card_id_to_int(card_id)
    source_column_id = _get_card_column_id(conn, card_id_int)
    target_column_id_int = _column_id_to_int(target_column_id)

    source_ids = _card_ids_in_column(conn, source_column_id)
    source_ids.remove(card_id_int)

    if source_column_id == target_column_id_int:
        target_ids = source_ids
    else:
        target_ids = _card_ids_in_column(conn, target_column_id_int)

    clamped_index = max(0, min(index, len(target_ids)))
    target_ids.insert(clamped_index, card_id_int)

    if source_column_id != target_column_id_int:
        _renumber_column(conn, source_column_id, source_ids)
    _renumber_column(conn, target_column_id_int, target_ids)
    conn.commit()


def apply_ai_action(conn: sqlite3.Connection, action: dict[str, Any]) -> None:
    """Apply one AI-proposed board action. Raises NotFoundError for unknown
    types or ids that don't exist -- callers should skip failed actions
    rather than aborting the whole chat turn."""
    action_type = action.get("type")

    if action_type == "add_card":
        add_card(
            conn,
            action["column_id"],
            action.get("title") or "Untitled",
            action.get("details") or "",
        )
    elif action_type == "update_card":
        update_card(conn, action["card_id"], action.get("title"), action.get("details"))
    elif action_type == "delete_card":
        delete_card(conn, action["card_id"])
    elif action_type == "move_card":
        move_card(
            conn, action["card_id"], action["column_id"], action.get("index") or 0
        )
    elif action_type == "rename_column":
        rename_column(conn, action["column_id"], action.get("title") or "")
    else:
        raise NotFoundError(f"Unknown AI action type: {action_type}")
