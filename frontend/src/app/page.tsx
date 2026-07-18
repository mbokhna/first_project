"use client";

import { useEffect, useState } from "react";
import { KanbanBoard } from "@/components/KanbanBoard";
import { LoginForm } from "@/components/LoginForm";
import { getSession, login, logout } from "@/lib/api";

export default function Home() {
  const [authenticated, setAuthenticated] = useState<boolean | null>(null);

  useEffect(() => {
    getSession().then(setAuthenticated);
  }, []);

  const handleLogin = async (username: string, password: string) => {
    const success = await login(username, password);
    if (success) {
      setAuthenticated(true);
    }
    return success;
  };

  const handleLogout = async () => {
    await logout();
    setAuthenticated(false);
  };

  if (authenticated === null) {
    return null;
  }

  if (!authenticated) {
    return <LoginForm onSubmit={handleLogin} />;
  }

  return <KanbanBoard onLogout={handleLogout} />;
}
