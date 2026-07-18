# Backend

FastAPI app managed with `uv`.

- `app/main.py` — FastAPI app.
  - `GET /api/health` — returns `{"status": "ok"}`.
  - `POST /api/login` — body `{username, password}`; hardcoded demo credentials `user`/`password` (see `DEMO_USERNAME`/`DEMO_PASSWORD`). On success, sets `user` in a signed session cookie (via Starlette `SessionMiddleware`, secret from `SESSION_SECRET` env var). 401 on bad credentials.
  - `POST /api/logout` — clears the session.
  - `GET /api/session` — returns `{"authenticated": bool}` based on the session cookie.
  - Everything else is mounted as static files from `static/` (the built Next.js frontend in Docker; a hello-world placeholder for local non-Docker dev).
  - CORS is enabled for `http://localhost:3000` with credentials, in case the frontend is ever run separately in dev — but see the note in `frontend/AGENTS.md`: dev mode (`npm run dev`) has no backend behind it by default, so the supported way to exercise login end-to-end is via Docker (same origin).
- `static/` — static files served at `/`.
- `tests/test_auth.py` — pytest coverage for the login/session/logout cycle (`uv run pytest`).
- `pyproject.toml` / `uv.lock` — dependencies (`fastapi`, `uvicorn[standard]`, `itsdangerous`), dev deps (`pytest`, `httpx`), Python 3.12.

## Local dev (without Docker)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
uv run pytest
```

## Via Docker

Use `scripts/start.sh` / `scripts/start.bat` from the project root (see `scripts/AGENTS.md`). Reads `SESSION_SECRET` (and later `OPENROUTER_API_KEY`) from the root `.env`.
