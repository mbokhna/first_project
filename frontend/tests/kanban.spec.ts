import { expect, test, type Page } from "@playwright/test";

const login = async (page: Page) => {
  await page.goto("/");
  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("password");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
};

test("requires login before showing the board", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();

  await page.getByLabel("Username").fill("user");
  await page.getByLabel("Password").fill("wrong");
  await page.getByRole("button", { name: /sign in/i }).click();
  await expect(page.getByText("Invalid username or password.")).toBeVisible();
});

test("logs in and out", async ({ page }) => {
  await login(page);
  await page.getByRole("button", { name: /log out/i }).click();
  await expect(page.getByRole("heading", { name: "Sign in" })).toBeVisible();
});

test("loads the kanban board with the five default columns", async ({ page }) => {
  await login(page);
  await expect(page.locator('[data-testid^="column-"]')).toHaveCount(5);
});

test("adds a card and it persists after reload", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  await firstColumn.getByRole("button", { name: /add a card/i }).click();
  await firstColumn.getByPlaceholder("Card title").fill("Playwright card");
  await firstColumn.getByPlaceholder("Details").fill("Added via e2e.");
  await firstColumn.getByRole("button", { name: /add card/i }).click();
  await expect(firstColumn.getByText("Playwright card")).toBeVisible();

  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(page.getByText("Playwright card")).toBeVisible();
});

test("renames a column and it persists after reload", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  const titleInput = firstColumn.getByLabel("Column title");
  await titleInput.fill("Renamed Column");
  await Promise.all([
    page.waitForResponse(
      (res) =>
        res.url().includes("/api/board/columns/") &&
        res.request().method() === "PATCH"
    ),
    titleInput.blur(),
  ]);

  await page.reload();
  await expect(page.getByRole("heading", { name: "Kanban Studio" })).toBeVisible();
  await expect(
    page.locator('[data-testid^="column-"]').first().getByLabel("Column title")
  ).toHaveValue("Renamed Column");
});

test("moves a card between columns", async ({ page }) => {
  await login(page);
  const columns = page.locator('[data-testid^="column-"]');
  const sourceColumn = columns.nth(0);
  const targetColumn = columns.nth(3);

  await sourceColumn.getByRole("button", { name: /add a card/i }).click();
  await sourceColumn.getByPlaceholder("Card title").fill("Card to move");
  await sourceColumn.getByRole("button", { name: /add card/i }).click();

  const card = page
    .locator('[data-testid^="card-"]')
    .filter({ hasText: "Card to move" });
  await expect(card).toBeVisible();

  const cardBox = await card.boundingBox();
  const columnBox = await targetColumn.boundingBox();
  if (!cardBox || !columnBox) {
    throw new Error("Unable to resolve drag coordinates.");
  }

  await page.mouse.move(
    cardBox.x + cardBox.width / 2,
    cardBox.y + cardBox.height / 2
  );
  await page.mouse.down();
  await page.mouse.move(
    columnBox.x + columnBox.width / 2,
    columnBox.y + 120,
    { steps: 12 }
  );
  await page.mouse.up();

  await expect(targetColumn.getByText("Card to move")).toBeVisible();
});

test("AI chat can add a card to the board", async ({ page }) => {
  await login(page);
  const firstColumn = page.locator('[data-testid^="column-"]').first();
  const columnId = await firstColumn.getAttribute("data-testid");

  const chatInput = page.getByLabel("Chat message");
  await chatInput.fill(
    `Add a card titled "AI e2e card" to the column with id ${columnId?.replace(
      "column-",
      ""
    )}.`
  );
  await page.getByRole("button", { name: /send/i }).click();

  await expect(page.getByTestId("chat-message-assistant")).toBeVisible({
    timeout: 30_000,
  });
  await expect(firstColumn.getByText("AI e2e card")).toBeVisible({
    timeout: 30_000,
  });
});
