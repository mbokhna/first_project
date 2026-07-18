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
