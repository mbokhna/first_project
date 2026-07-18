# Database

SQLite, created automatically on first run if the file doesn't exist (`backend/data/app.db`, see Part 6).

## Schema

See [`schema.json`](./schema.json) for the full column-level definition. Summary:

```
users (id, username, created_at)
  └─< boards (id, user_id, created_at)          -- MVP: exactly one board per user
        └─< kanban_columns (id, board_id, title, position)
              └─< cards (id, column_id, title, details, position)
```

- **`users`** — MVP has a single seeded row (`username = "user"`), created on first backend startup if missing. Login (Part 4) still checks the hardcoded `user`/`password` credentials rather than querying this table — the table exists so multi-user support is a schema-compatible addition later, per the root `AGENTS.md` MVP limitations.
- **`boards`** — one row per user, enforced with `UNIQUE(user_id)` for the MVP's "1 board per user" rule.
- **`kanban_columns`** — the board's columns (Backlog, Discovery, etc.), ordered by `position`. Renamed from the frontend's `Column` type to avoid confusion with the SQL term "column."
- **`cards`** — cards within a column, ordered by `position` within their column.

## Why `position` instead of the frontend's `cardIds` arrays

The current frontend (`frontend/src/lib/kanban.ts`) models order as an array of card ids on each column. SQL has no native ordered-list type, so each card/column instead stores an integer `position`; the API (Part 6) returns rows ordered by `position` and reconstructs the same `BoardData` shape (`columns` + `cards` record) the frontend already expects, so `frontend/src/lib/kanban.ts`'s types and `moveCard` logic don't need to change — only where the data comes from does (API instead of `initialData`).

## Seeding

On first run, if no user exists, the backend creates: the `user` row, one `boards` row for them, and 5 `kanban_columns` (Backlog, Discovery, In Progress, Review, Done) with no cards — matching the fixed-columns requirement in the root `AGENTS.md`. This replaces the frontend's hardcoded `initialData` sample cards, which were only ever a design placeholder.
