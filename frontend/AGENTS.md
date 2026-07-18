# Frontend — existing code

## Stack

- Next.js 16 (App Router), React 19, TypeScript
- Tailwind CSS 4 (via `@tailwindcss/postcss`), custom CSS variables for the color scheme
- Drag and drop: `@dnd-kit/core`, `@dnd-kit/sortable`, `@dnd-kit/utilities`
- Unit/component tests: Vitest + Testing Library (jsdom)
- End-to-end tests: Playwright

## Structure

- `src/app/layout.tsx` — root layout, loads Space Grotesk (display font) and Manrope (body font), sets page metadata.
- `src/app/page.tsx` — renders `<KanbanBoard />` at `/`. This is the only route.
- `src/app/globals.css` — Tailwind import plus the color scheme as CSS variables (`--accent-yellow`, `--primary-blue`, `--secondary-purple`, `--navy-dark`, `--gray-text`, `--surface`, etc.), matching the palette in the root `AGENTS.md`.
- `src/lib/kanban.ts` — pure data/logic, no React:
  - Types: `Card`, `Column`, `BoardData`.
  - `initialData` — hardcoded demo board (5 columns: Backlog, Discovery, In Progress, Review, Done; 8 sample cards).
  - `moveCard(columns, activeId, overId)` — reorders/relocates a card given drag-and-drop ids; pure function, returns new columns array.
  - `createId(prefix)` — generates a pseudo-unique id for new cards.
  - Covered by `src/lib/kanban.test.ts`.
- `src/components/KanbanBoard.tsx` — top-level client component (`"use client"`). Owns all board state via `useState<BoardData>`, wires up `@dnd-kit` `DndContext`/`DragOverlay`, and handles rename/add/delete/move. No persistence — state resets on page reload, no API calls.
- `src/components/KanbanColumn.tsx` — one column: droppable area, editable title input, renders cards via `SortableContext`, embeds `NewCardForm`.
- `src/components/KanbanCard.tsx` — one draggable card (`useSortable`), shows title/details, has a delete button.
- `src/components/KanbanCardPreview.tsx` — static, non-interactive render of a card used inside `DragOverlay` while dragging.
- `src/components/NewCardForm.tsx` — inline toggle form (title + details) inside a column footer to add a card.

## What this is / isn't

- The board itself is still a **frontend-only demo**: no auth/login, no fetch calls, no database yet. All data lives in memory (`initialData` + local component state).
- `next.config.ts` uses `output: "export"` — `npm run build` produces a static `out/` directory with no Node server required. The root `Dockerfile` builds this and copies `out/` into the FastAPI backend's `static/` folder, which serves it at `/` (see Part 3 in `docs/PLAN.md`).
- No client-side routing, `next/image`, or other features that are incompatible with static export are used, so this conversion was drop-in.
- SQLite persistence and the AI chat are not wired in yet — those come in later plan parts.
- `data-testid` attributes (`column-<id>`, `card-<id>`) are already in place and used by both Playwright e2e tests and future automation.

## Auth

- `src/app/page.tsx` is a client component that checks `GET /api/session` on mount and renders either `LoginForm` or `KanbanBoard`.
- `src/components/LoginForm.tsx` posts to `/api/login`; `src/lib/api.ts` wraps `login`/`logout`/`getSession` fetch calls (`credentials: "include"` so the backend's session cookie is sent/stored).
- `KanbanBoard` takes an optional `onLogout` prop; when provided it renders a "Log out" button that calls `/api/logout`.
- **Important:** these fetch calls hit the FastAPI backend at the same origin. `npm run dev` (port 3000) has no backend behind it, so login will always fail there — the app must be tested via the Docker container (`scripts/start.sh`), which serves frontend and backend from the same origin on port 8000. `frontend/tests/kanban.spec.ts` runs against that container by setting `PLAYWRIGHT_TEST_BASE_URL=http://localhost:8000` (see `playwright.config.ts`).

## Testing

```bash
npm run test:unit   # Vitest — src/lib/kanban.test.ts, src/components/KanbanBoard.test.tsx
npm run test:e2e    # Playwright — tests/kanban.spec.ts (needs the dev/build server running per playwright.config.ts)
npm run test:all    # both
```

## Scripts

```bash
npm install
npm run dev     # local dev server
npm run build    # production build
npm run start    # serve production build
npm run lint     # eslint
```
