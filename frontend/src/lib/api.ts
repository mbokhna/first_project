import type { BoardData } from "@/lib/kanban";

export const login = async (username: string, password: string): Promise<boolean> => {
  const response = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    credentials: "include",
    body: JSON.stringify({ username, password }),
  });
  return response.ok;
};

export const logout = async (): Promise<void> => {
  await fetch("/api/logout", { method: "POST", credentials: "include" });
};

export const getSession = async (): Promise<boolean> => {
  const response = await fetch("/api/session", { credentials: "include" });
  if (!response.ok) {
    return false;
  }
  const data = (await response.json()) as { authenticated: boolean };
  return data.authenticated;
};

const boardRequest = async (
  path: string,
  init?: RequestInit
): Promise<BoardData> => {
  const response = await fetch(path, {
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with ${response.status}`);
  }
  return (await response.json()) as BoardData;
};

export const getBoard = (): Promise<BoardData> => boardRequest("/api/board");

export const renameColumn = (
  columnId: string,
  title: string
): Promise<BoardData> =>
  boardRequest(`/api/board/columns/${columnId}`, {
    method: "PATCH",
    body: JSON.stringify({ title }),
  });

export const addCard = (
  columnId: string,
  title: string,
  details: string
): Promise<BoardData> =>
  boardRequest("/api/board/cards", {
    method: "POST",
    body: JSON.stringify({ column_id: columnId, title, details }),
  });

export const deleteCard = (cardId: string): Promise<BoardData> =>
  boardRequest(`/api/board/cards/${cardId}`, { method: "DELETE" });

export const moveCardApi = (
  cardId: string,
  columnId: string,
  index: number
): Promise<BoardData> =>
  boardRequest(`/api/board/cards/${cardId}/move`, {
    method: "POST",
    body: JSON.stringify({ column_id: columnId, index }),
  });

export type ChatMessage = {
  role: "user" | "assistant";
  content: string;
};

export type ChatResult = {
  reply: string;
  board: BoardData;
};

export const sendChatMessage = async (
  message: string,
  history: ChatMessage[]
): Promise<ChatResult> => {
  const response = await fetch("/api/ai/chat", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, history }),
  });
  if (!response.ok) {
    throw new Error(`Chat request failed with ${response.status}`);
  }
  return (await response.json()) as ChatResult;
};
