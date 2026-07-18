import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";
import Home from "@/app/page";

const mockFetch = (authenticated: boolean, loginOk: boolean) => {
  vi.stubGlobal(
    "fetch",
    vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/api/session")) {
        return new Response(JSON.stringify({ authenticated }), { status: 200 });
      }
      if (url.endsWith("/api/login")) {
        return new Response(null, { status: loginOk ? 200 : 401 });
      }
      if (url.endsWith("/api/logout")) {
        return new Response(null, { status: 200 });
      }
      if (url.endsWith("/api/board")) {
        return new Response(
          JSON.stringify({ columns: [], cards: {} }),
          { status: 200 }
        );
      }
      throw new Error(`Unexpected fetch: ${url} ${init?.method ?? "GET"}`);
    })
  );
};

describe("Home page auth gate", () => {
  beforeEach(() => {
    vi.unstubAllGlobals();
  });

  it("shows the login form when not authenticated", async () => {
    mockFetch(false, true);
    render(<Home />);
    expect(
      await screen.findByRole("heading", { name: "Sign in" })
    ).toBeInTheDocument();
  });

  it("shows the board when already authenticated", async () => {
    mockFetch(true, true);
    render(<Home />);
    expect(await screen.findByText("Kanban Studio")).toBeInTheDocument();
  });

  it("shows an error on invalid credentials", async () => {
    mockFetch(false, false);
    render(<Home />);
    await screen.findByRole("heading", { name: "Sign in" });

    await userEvent.type(screen.getByLabelText("Username"), "user");
    await userEvent.type(screen.getByLabelText("Password"), "wrong");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Invalid username or password."
    );
  });

  it("logs in and then logs out", async () => {
    mockFetch(false, true);
    render(<Home />);
    await screen.findByRole("heading", { name: "Sign in" });

    await userEvent.type(screen.getByLabelText("Username"), "user");
    await userEvent.type(screen.getByLabelText("Password"), "password");
    await userEvent.click(screen.getByRole("button", { name: /sign in/i }));

    await screen.findByText("Kanban Studio");

    await userEvent.click(screen.getByRole("button", { name: /log out/i }));

    await waitFor(() =>
      expect(
        screen.getByRole("heading", { name: "Sign in" })
      ).toBeInTheDocument()
    );
  });
});
