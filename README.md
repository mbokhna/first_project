# Project Management MVP

A small Kanban board app: sign in, manage one board with drag-and-drop cards,
and ask an AI assistant in the sidebar to create, edit, or move cards for
you. Runs locally in a single Docker container (NextJS frontend + FastAPI
backend + SQLite).

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (running)
- Git

## Setup

1. Clone this repository.
2. Copy `.env.example` to `.env` and fill in the values:
   - `SESSION_SECRET` — any random string.
   - `OPENROUTER_API_KEY` — free key from [openrouter.ai](https://openrouter.ai) (only needed for the AI chat; the board itself works without it).

## Run

```
./scripts/start.sh
```

(Windows: `scripts\start.bat`)

Open [http://localhost:8000](http://localhost:8000) and log in with:

- Username: `user`
- Password: `password`

## Stop

```
./scripts/stop.sh
```

(Windows: `scripts\stop.bat`)

## More details

See [`docs/PLAN.md`](docs/PLAN.md) for how this was built, and the
`AGENTS.md` files in the root, `frontend/`, and `backend/` directories for
technical details on each part.
