import sqlite3
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_PATH = DB_DIR / "app.db"

DEFAULT_USERNAME = "user"
DEFAULT_COLUMN_TITLES = ["Backlog", "Discovery", "In Progress", "Review", "Done"]

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS boards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS kanban_columns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    board_id INTEGER NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    position INTEGER NOT NULL
);
CREATE TABLE IF NOT EXISTS cards (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    column_id INTEGER NOT NULL REFERENCES kanban_columns(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    details TEXT NOT NULL DEFAULT '',
    position INTEGER NOT NULL
);
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    _seed_default_user(conn)
    conn.commit()


def _seed_default_user(conn: sqlite3.Connection) -> None:
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (DEFAULT_USERNAME,)
    ).fetchone()
    if existing is not None:
        return

    cursor = conn.execute(
        "INSERT INTO users (username) VALUES (?)", (DEFAULT_USERNAME,)
    )
    user_id = cursor.lastrowid

    cursor = conn.execute("INSERT INTO boards (user_id) VALUES (?)", (user_id,))
    board_id = cursor.lastrowid

    for position, title in enumerate(DEFAULT_COLUMN_TITLES):
        conn.execute(
            "INSERT INTO kanban_columns (board_id, title, position) VALUES (?, ?, ?)",
            (board_id, title, position),
        )
