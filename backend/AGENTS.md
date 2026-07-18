# Backend

FastAPI app managed with `uv`.

- `app/main.py` — FastAPI app. `GET /api/health` returns `{"status": "ok"}`. Everything else is mounted as static files from `static/` (currently a hello-world placeholder; Part 3 replaces this with the built Next.js frontend).
- `static/` — static files served at `/`.
- `pyproject.toml` / `uv.lock` — dependencies (`fastapi`, `uvicorn[standard]`), Python 3.12.

## Local dev (without Docker)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

## Via Docker

Use `scripts/start.sh` / `scripts/start.bat` from the project root (see `scripts/AGENTS.md`).
