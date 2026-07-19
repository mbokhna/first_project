# Backend

FastAPI app managed with `uv`.

- `app/main.py` — FastAPI app.
  - `GET /api/health` — returns `{"status": "ok"}`.
  - `POST /api/login` — body `{username, password}`; hardcoded demo credentials `user`/`password` (see `DEMO_USERNAME`/`DEMO_PASSWORD`). On success, sets `user` in a signed session cookie (via Starlette `SessionMiddleware`, secret from `SESSION_SECRET` env var). 401 on bad credentials.
  - `POST /api/logout` — clears the session.
  - `GET /api/session` — returns `{"authenticated": bool}` based on the session cookie.
  - `GET /api/board`, `PATCH /api/board/columns/{column_id}`, `POST /api/board/cards`, `PATCH /api/board/cards/{card_id}`, `DELETE /api/board/cards/{card_id}`, `POST /api/board/cards/{card_id}/move` — all require a logged-in session (401 otherwise) and return the full board (same `{columns, cards}` shape the frontend's `BoardData` type expects) after applying the change.
  - `GET /api/ai/ping` — connectivity smoke test for Part 8: asks the AI "what is 2+2" via `app/ai.py` and returns `{"reply": ...}`. Requires login. 503 if `OPENROUTER_API_KEY` isn't set.
  - Everything else is mounted as static files from `static/` (the built Next.js frontend in Docker; a hello-world placeholder for local non-Docker dev).
  - CORS is enabled for `http://localhost:3000` with credentials, in case the frontend is ever run separately in dev — but see the note in `frontend/AGENTS.md`: dev mode (`npm run dev`) has no backend behind it by default, so the supported way to exercise login/the board end-to-end is via Docker (same origin).
  - Loads the root `.env` at startup via `python-dotenv` (`load_dotenv(...)` at the top of `main.py`), so `SESSION_SECRET`/`OPENROUTER_API_KEY` are picked up for local non-Docker runs too, not just `docker run --env-file .env`.
- `app/ai.py` — OpenRouter client (OpenAI-compatible API, `base_url="https://openrouter.ai/api/v1"`, `api_key` from `OPENROUTER_API_KEY`). `DEFAULT_MODEL = "openai/gpt-oss-20b:free"` — **deviates from the root `AGENTS.md`'s `openai/gpt-oss-120b`**: OpenRouter retired the free tier of the 120b model (confirmed via a live 404 from their API telling us to use the paid slug instead), so we're using the free 20b sibling instead, per explicit user instruction to avoid any billing/credits. Override with the `OPENROUTER_MODEL` env var if a paid model is ever wanted.
- `app/db.py` — SQLite connection + schema (`users`, `boards`, `kanban_columns`, `cards`, see `docs/schema.json`) and startup seeding (one `user` row, one board, 5 default columns) if the DB is empty. DB file at `backend/data/app.db`, created automatically. **A fresh `sqlite3.Connection` is opened per request** (see `get_db` in `main.py`) — `sqlite3.Connection` objects aren't safe to share across threads, and FastAPI runs sync route handlers in a threadpool.
- `app/board.py` — board read/write logic against the DB (id mapping between DB integer ids and the frontend's `col-<id>`/`card-<id>` string ids, card/column ordering via an integer `position` column, `NotFoundError` for missing rows).
- `static/` — static files served at `/`.
- `tests/conftest.py` — `client` fixture: fresh temp-file SQLite DB per test, overrides `get_db` so tests never touch the real dev database.
- `tests/test_auth.py`, `tests/test_board.py` — pytest coverage for login/session/logout and all board CRUD + move/reorder routes (`uv run pytest`).
- `tests/test_ai.py` — live connectivity test against the real OpenRouter API (asks "2+2", asserts "4" in the reply). Auto-skipped if `OPENROUTER_API_KEY` isn't set (e.g. CI without a key), so it never blocks the rest of the suite.
- `pyproject.toml` / `uv.lock` — dependencies (`fastapi`, `uvicorn[standard]`, `itsdangerous`, `openai`, `python-dotenv`), dev deps (`pytest`, `httpx`), Python 3.12.

## Local dev (without Docker)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
uv run pytest
```

## Via Docker

Use `scripts/start.sh` / `scripts/start.bat` from the project root (see `scripts/AGENTS.md`). Reads `SESSION_SECRET` (and later `OPENROUTER_API_KEY`) from the root `.env`.
