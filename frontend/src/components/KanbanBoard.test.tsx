import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import { KanbanBoard } from "@/components/KanbanBoard";
import type { BoardData } from "@/lib/kanban";

const getFirstColumn = () => screen.getAllByTestId(/column-/i)[0];

const mockBoardServer = () => {
  let board: BoardData = {
    columns: [
      { id: "col-1", title: "Backlog", cardIds: [] },
      { id: "col-2", title: "Discovery", cardIds: [] },
      { id: "col-3", title: "In Progress", cardIds: [] },
      { id: "col-4", title: "Review", cardIds: [] },
      { id: "col-5", title: "Done", cardIds: [] },
    ],
    cards: {},
  };
  let nextCardId = 1;

  const respond = (body: unknown) =>
    Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? "GET";
      const body = init?.body ? JSON.parse(init.body as string) : undefined;

      if (url.endsWith("/api/board") && method === "GET") {
        return respond(board);
      }

      if (url.includes("/api/board/columns/") && method === "PATCH") {
        const columnId = url.split("/api/board/columns/")[1];
        board = {
          ...board,
          columns: board.columns.map((column) =>
            column.id === columnId
              ? { ...column, title: body.title }
              : column
          ),
        };
        return respond(board);
      }

      if (url.endsWith("/api/board/cards") && method === "POST") {
        const id = `card-${nextCardId++}`;
        board = {
          columns: board.columns.map((column) =>
            column.id === body.column_id
              ? { ...column, cardIds: [...column.cardIds, id] }
              : column
          ),
          cards: {
            ...board.cards,
            [id]: { id, title: body.title, details: body.details },
          },
        };
        return respond(board);
      }

      if (url.includes("/api/board/cards/") && method === "DELETE") {
        const cardId = url.split("/api/board/cards/")[1];
        // eslint-disable-next-line @typescript-eslint/no-unused-vars
        const { [cardId]: _removed, ...remainingCards } = board.cards;
        board = {
          columns: board.columns.map((column) => ({
            ...column,
            cardIds: column.cardIds.filter((id) => id !== cardId),
          })),
          cards: remainingCards,
        };
        return respond(board);
      }

      if (url.endsWith("/api/ai/chat") && method === "POST") {
        if (/add a card/i.test(body.message)) {
          const id = `card-${nextCardId++}`;
          board = {
            columns: board.columns.map((column, index) =>
              index === 0
                ? { ...column, cardIds: [...column.cardIds, id] }
                : column
            ),
            cards: {
              ...board.cards,
              [id]: { id, title: "AI added card", details: "" },
            },
          };
          return respond({ reply: "Added the card.", board });
        }
        return respond({ reply: `Echo: ${body.message}`, board });
      }

      throw new Error(`Unhandled request: ${method} ${url}`);
    })
  );
};

describe("KanbanBoard", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
    mockBoardServer();
  });

  it("renders five columns", async () => {
    render(<KanbanBoard />);
    expect(await screen.findAllByTestId(/column-/i)).toHaveLength(5);
  });

  it("renames a column", async () => {
    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);
    const column = getFirstColumn();
    const input = within(column).getByLabelText("Column title");
    await userEvent.clear(input);
    await userEvent.type(input, "New Name");
    input.blur();

    expect(await within(column).findByDisplayValue("New Name")).toBeInTheDocument();
  });

  it("adds and removes a card", async () => {
    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);
    const column = getFirstColumn();
    const addButton = within(column).getByRole("button", {
      name: /add a card/i,
    });
    await userEvent.click(addButton);

    const titleInput = within(column).getByPlaceholderText(/card title/i);
    await userEvent.type(titleInput, "New card");
    const detailsInput = within(column).getByPlaceholderText(/details/i);
    await userEvent.type(detailsInput, "Notes");

    await userEvent.click(within(column).getByRole("button", { name: /add card/i }));

    expect(await within(column).findByText("New card")).toBeInTheDocument();

    const deleteButton = within(column).getByRole("button", {
      name: /delete new card/i,
    });
    await userEvent.click(deleteButton);

    expect(within(column).queryByText("New card")).not.toBeInTheDocument();
  });

  it("sends a chat message and shows the reply", async () => {
    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);

    const chatInput = screen.getByLabelText("Chat message");
    await userEvent.type(chatInput, "Hello there");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText("Hello there")).toBeInTheDocument();
    expect(await screen.findByText("Echo: Hello there")).toBeInTheDocument();
  });

  it("applies a board update returned from the chat", async () => {
    render(<KanbanBoard />);
    await screen.findAllByTestId(/column-/i);

    const chatInput = screen.getByLabelText("Chat message");
    await userEvent.type(chatInput, "Please add a card for testing");
    await userEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText("AI added card")).toBeInTheDocument();
  });
});
