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

- This is a **frontend-only demo**: no backend, no auth/login, no fetch calls, no database. All data lives in memory (`initialData` + local component state).
- Not yet wired to Docker, FastAPI, SQLite, or the AI chat — those come in later plan parts.
- `data-testid` attributes (`column-<id>`, `card-<id>`) are already in place and used by both Playwright e2e tests and future automation.

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
