# High level steps for project

Detailed plan below. Each part has a checklist of substeps (to be checked off as completed), plus tests and success criteria. Work through parts in order; each part should be fully done, tested, and approved before moving to the next.

## Part 1: Plan

- [x] Enrich this document with substeps, tests, and success criteria for every part.
- [x] Create `frontend/AGENTS.md` describing the existing frontend code.
- [ ] User reviews and approves this plan.

**Success criteria:** user has read this document and explicitly approved it before Part 2 starts.

## Part 2: Scaffolding

- [x] Create `backend/` as a Python project managed with `uv` (`uv init`, add `fastapi`, `uvicorn`).
- [x] Add a minimal FastAPI app with a `GET /api/health` (or similar) route returning JSON, and a route serving a static "hello world" HTML page at `/`.
- [x] Write a `Dockerfile` at the project root that builds the backend (and later will serve the frontend build).
- [x] Write `scripts/start.sh` (Mac/Linux), `scripts/start.bat` (Windows), and stop equivalents (`scripts/stop.sh`, `scripts/stop.bat`) that build/run and stop the Docker container.
- [x] Update `backend/AGENTS.md` with a real description of the backend.

Note: the AI chat parts (8-10) are deferred until the rest of the app (Parts 2-7) is done, to avoid registering/funding OpenRouter until it's actually needed.

**Tests:** manual — run the start script, hit `/` in a browser and confirm the hello-world page loads, hit the API route and confirm a JSON response.

**Success criteria:** `scripts/start` brings up a Docker container serving a static hello-world page at `/` and a working API route; `scripts/stop` cleanly stops it.

## Part 3: Add in Frontend

- [x] Configure the FastAPI backend to statically build the Next.js app (`next build`) and serve the output at `/`.
- [x] Confirm the existing Kanban demo (from `frontend/`) renders correctly when served this way, not just via `next dev`.
- [x] Add/confirm frontend unit tests (Vitest) and integration/e2e tests (Playwright) run against the built, backend-served app.

**Tests:** `npm run test:unit`, `npm run test:e2e` (pointed at the Dockerized app), plus a manual check that `/` shows the Kanban board through the backend, not the Next dev server.

**Success criteria:** visiting `/` on the running Docker container shows the full Kanban board demo with drag-and-drop working; all frontend tests pass.

## Part 4: Add in a fake user sign in experience

- [ ] Add a login page/screen requiring hardcoded credentials (`user` / `password`) before the Kanban board is shown.
- [ ] Add a logout action that returns to the login screen.
- [ ] Decide and implement session handling for the MVP (e.g. simple cookie/token issued by the backend on login).
- [ ] Protect the Kanban route/API so it isn't visible without being "logged in".

**Tests:** unit tests for the login form/validation; e2e tests for: visiting `/` while logged out shows login, wrong credentials are rejected, correct credentials show the board, logout returns to login.

**Success criteria:** a fresh visitor cannot see the Kanban board without logging in with `user`/`password`; logout works; all new tests pass alongside existing ones.

## Part 5: Database modeling

- [ ] Propose a database schema for users, boards, columns, and cards (as JSON in `docs/`, e.g. `docs/schema.json` or `docs/DATABASE.md`).
- [ ] Document the approach: tables/entities, relationships, how the MVP's "1 board per user" constraint is represented while allowing multiple users/boards in the future.
- [ ] Get explicit user sign-off on the schema before implementing it.

**Tests:** none (design step) — reviewed by the user instead.

**Success criteria:** user has reviewed and approved the schema document before Part 6 starts.

## Part 6: Backend

- [ ] Implement the SQLite database using the approved schema; create the DB file on first run if it doesn't exist.
- [ ] Add API routes to read a user's Kanban board and to change it (rename column, add/edit/delete/move card).
- [ ] Write backend unit tests covering each route, including edge cases (missing board, invalid ids, etc.).

**Tests:** `pytest` (or equivalent) covering all new routes and DB logic; run against a throwaway/test SQLite DB.

**Success criteria:** all backend unit tests pass; a fresh checkout with no existing DB file boots cleanly and creates one automatically.

## Part 7: Frontend + Backend

- [ ] Replace the frontend's in-memory `initialData`/local state with real calls to the backend API for load and every mutation (rename, add, delete, move).
- [ ] Handle loading and error states in the UI.
- [ ] Confirm state persists across page reloads and logins.

**Tests:** update/extend Vitest unit tests for API-integrated components; extend Playwright e2e tests to verify persistence (reload the page and confirm changes survive).

**Success criteria:** the Kanban board is fully persistent — reloading the page or logging back in shows the same state; all tests pass.

## Part 8: AI connectivity

- [ ] Add OpenRouter client setup in the backend, reading `OPENROUTER_API_KEY` from `.env`.
- [ ] Add a simple backend test route/function that asks the AI "what is 2+2" and checks the response, to confirm connectivity end-to-end using `openai/gpt-oss-120b`.

**Tests:** an automated (or documented manual) test that calls the AI and asserts a sane response to "2+2".

**Success criteria:** the "2+2" test call succeeds and returns a correct-looking answer, confirming API key and model wiring work.

## Part 9: AI + Kanban context

- [ ] Extend the backend AI call to always include the current board as JSON, the user's message, and conversation history in the prompt/context.
- [ ] Use Structured Outputs so the AI responds with a natural-language reply plus an optional Kanban update payload.
- [ ] Apply any returned Kanban update to the database.

**Tests:** backend tests with mocked/real AI responses verifying: a plain question returns a reply with no board change; a request like "add a card to Done" returns a structured update that correctly mutates the board.

**Success criteria:** the backend reliably parses Structured Outputs and applies board updates only when the AI includes them; tests pass.

## Part 10: AI chat UI

- [ ] Add a sidebar widget with a full chat UI (message history, input box) styled per the project's color scheme.
- [ ] Wire the sidebar to the Part 9 backend endpoint.
- [ ] When the AI response includes a Kanban update, refresh the board UI automatically without a manual page reload.

**Tests:** Playwright e2e test that sends a chat message requesting a board change and asserts the board UI updates accordingly; unit tests for the chat component's message rendering.

**Success criteria:** a user can chat in the sidebar, ask the AI to create/edit/move a card, and see the Kanban board update live, matching the business requirements in the root `AGENTS.md`.
