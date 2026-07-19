# Backend

FastAPI app managed with `uv`. Linted/formatted with `ruff` (`uv run ruff check .`, `uv run ruff format .`).

## Structure

- `app/main.py` — application factory (`create_app()`). Loads the root `.env`, builds the `FastAPI` instance, adds `SessionMiddleware`/`CORSMiddleware`, initializes the DB, includes the routers below, mounts `static/`. `app = create_app()` at the bottom is what `uvicorn app.main:app` serves.
- `app/config.py` — path constants (`STATIC_DIR`, `ENV_FILE`), demo credentials (`DEMO_USERNAME`/`DEMO_PASSWORD`), `get_session_secret()` (reads `SESSION_SECRET` env var, read lazily so it's called only after `.env` is loaded).
- `app/deps.py` — shared FastAPI dependencies: `get_db` (yields a fresh `sqlite3.Connection` per request — see note below) and `require_user` (401s if there's no session).
- `app/schemas.py` — all Pydantic request models (`LoginRequest`, `AddCardRequest`, `ChatRequest`, etc.).
- `app/routers/auth.py` — `GET /api/health`, `POST /api/login`, `POST /api/logout`, `GET /api/session`. Login sets `user` in a signed session cookie (Starlette `SessionMiddleware`); logout clears it.
- `app/routers/board.py` — `GET /api/board`, `PATCH /api/board/columns/{column_id}`, `POST /api/board/cards`, `PATCH /api/board/cards/{card_id}`, `DELETE /api/board/cards/{card_id}`, `POST /api/board/cards/{card_id}/move`. All require a logged-in session (401 otherwise) and return the full board (`{columns, cards}`, matching the frontend's `BoardData` type) after applying the change. Thin: each route just calls into `app/board.py` and translates `NotFoundError` to a 404.
- `app/routers/ai.py` — `GET /api/ai/ping` (connectivity smoke test, asks "what is 2+2") and `POST /api/ai/chat` (body `{message, history}`; sends the board + history to `app/ai.py:chat()`, applies any returned actions via `app/board.py:apply_ai_action`, returns `{reply, board}`). Invalid actions (bad/missing ids, unknown type) are skipped rather than failing the whole request.
- `app/ai.py` — OpenRouter client (OpenAI-compatible API, `base_url="https://openrouter.ai/api/v1"`, `api_key` from `OPENROUTER_API_KEY`, read lazily inside functions so import order doesn't matter). `DEFAULT_MODEL = "openai/gpt-oss-20b:free"` — **deviates from the root `AGENTS.md`'s `openai/gpt-oss-120b`**: OpenRouter retired the free tier of the 120b model (confirmed via a live 404 from their API telling us to use the paid slug instead), so we're using the free 20b sibling instead, per explicit user instruction to avoid any billing/credits. Override with the `OPENROUTER_MODEL` env var if a paid model is ever wanted.
  - `ask(prompt)` — one-shot prompt/response, used by `/api/ai/ping`.
  - `chat(board, history, message)` — builds one system prompt (instructions + the board as JSON, explicitly telling the model every id it could need is already there so it never has to ask), sends history + the new message, and asks for a `{"reply", "actions"}` JSON object (`response_format={"type": "json_object"}` — the widely-supported JSON mode, not strict `json_schema`, since not all OpenRouter-hosted models support strict structured outputs). Strips a markdown code fence if the model wraps its JSON in one (`_extract_json_object`) before validating; falls back to `ChatReply(reply=<raw text>, actions=[])` if it still doesn't parse.
- `app/board.py` — board read/write logic against the DB: id mapping between DB integer ids and the frontend's `col-<id>`/`card-<id>` string ids, card/column ordering via an integer `position` column, `NotFoundError` for missing rows, plus `apply_ai_action(conn, action)` which dispatches one AI-proposed action dict to the matching mutation function by `type`.
- `app/db.py` — SQLite connection + schema (`users`, `boards`, `kanban_columns`, `cards`, see `docs/schema.json`) and startup seeding (one `user` row, one board, 5 default columns) if the DB is empty. DB file at `backend/data/app.db`, created automatically. **A fresh `sqlite3.Connection` is opened per request** (`get_db` in `app/deps.py`) — `sqlite3.Connection` objects aren't safe to share across threads, and FastAPI runs sync route handlers in a threadpool.
- `static/` — static files served at `/` (the built Next.js frontend in Docker; a hello-world placeholder for local non-Docker dev).
- `tests/conftest.py` — `client` fixture: fresh temp-file SQLite DB per test, overrides `get_db` (imported from `app.deps`) so tests never touch the real dev database.
- `tests/test_auth.py`, `tests/test_board.py` — pytest coverage for login/session/logout and all board CRUD + move/reorder routes.
- `tests/test_ai.py`, `tests/test_ai_chat.py` — live tests against the real OpenRouter API (connectivity, plain-question-leaves-board-alone, add-card-request-mutates-board). Auto-skipped if `OPENROUTER_API_KEY` isn't set, so they never block the rest of the suite.
- `pyproject.toml` / `uv.lock` — dependencies (`fastapi`, `uvicorn[standard]`, `itsdangerous`, `openai`, `python-dotenv`), dev deps (`pytest`, `httpx`, `ruff`), Python 3.12. `[tool.ruff]` config: line length 88, `select = ["E", "W", "F", "I", "N", "UP", "B", "SIM"]`; `app/ai.py` is exempt from `E501` (long lines) since it holds an intentionally long prompt template.

## Local dev (without Docker)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
uv run pytest
uv run ruff check .
uv run ruff format .
```

## Via Docker

Use `scripts/start.sh` / `scripts/start.bat` from the project root (see `scripts/AGENTS.md`). Reads `SESSION_SECRET` and `OPENROUTER_API_KEY` from the root `.env`.
