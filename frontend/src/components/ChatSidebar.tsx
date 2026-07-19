"use client";

import { useState, type FormEvent } from "react";
import type { ChatMessage } from "@/lib/api";

type ChatSidebarProps = {
  messages: ChatMessage[];
  onSend: (message: string) => Promise<void>;
};

export const ChatSidebar = ({ messages, onSend }: ChatSidebarProps) => {
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const trimmed = input.trim();
    if (!trimmed || sending) {
      return;
    }
    setSending(true);
    setError(false);
    setInput("");
    try {
      await onSend(trimmed);
    } catch {
      setError(true);
    } finally {
      setSending(false);
    }
  };

  return (
    <aside className="flex h-fit max-h-[calc(100vh-6rem)] w-full flex-col rounded-[32px] border border-[var(--stroke)] bg-white/80 p-6 shadow-[var(--shadow)] backdrop-blur lg:sticky lg:top-12 lg:w-[340px]">
      <p className="text-xs font-semibold uppercase tracking-[0.35em] text-[var(--gray-text)]">
        AI Assistant
      </p>
      <h2 className="mt-2 font-display text-xl font-semibold text-[var(--navy-dark)]">
        Ask about your board
      </h2>
      <p className="mt-2 text-sm leading-6 text-[var(--gray-text)]">
        Ask questions, or ask it to create, edit, or move cards for you.
      </p>

      <div
        className="mt-4 flex-1 space-y-3 overflow-y-auto pr-1"
        style={{ minHeight: "120px" }}
      >
        {messages.length === 0 && (
          <p className="text-sm text-[var(--gray-text)]">
            No messages yet. Try &quot;Add a card to Backlog about writing
            docs.&quot;
          </p>
        )}
        {messages.map((message, index) => (
          <div
            key={index}
            data-testid={`chat-message-${message.role}`}
            className={
              message.role === "user"
                ? "ml-6 rounded-2xl bg-[var(--secondary-purple)] px-4 py-2 text-sm text-white"
                : "mr-6 rounded-2xl bg-[var(--surface)] px-4 py-2 text-sm text-[var(--navy-dark)]"
            }
          >
            {message.content}
          </div>
        ))}
        {sending && (
          <div className="mr-6 rounded-2xl bg-[var(--surface)] px-4 py-2 text-sm text-[var(--gray-text)]">
            Thinking...
          </div>
        )}
      </div>

      {error && (
        <p className="mt-3 text-sm font-medium text-red-600" role="alert">
          Couldn&apos;t reach the AI assistant. Try again.
        </p>
      )}

      <form onSubmit={handleSubmit} className="mt-4 flex gap-2">
        <input
          value={input}
          onChange={(event) => setInput(event.target.value)}
          placeholder="Ask the assistant..."
          aria-label="Chat message"
          disabled={sending}
          className="w-full rounded-xl border border-[var(--stroke)] bg-white px-3 py-2 text-sm text-[var(--navy-dark)] outline-none transition focus:border-[var(--primary-blue)] disabled:opacity-60"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="rounded-full bg-[var(--secondary-purple)] px-4 py-2 text-xs font-semibold uppercase tracking-wide text-white transition hover:brightness-110 disabled:opacity-60"
        >
          Send
        </button>
      </form>
    </aside>
  );
};
