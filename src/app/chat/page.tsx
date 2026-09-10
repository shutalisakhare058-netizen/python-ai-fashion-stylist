"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import NavBar from "@/components/NavBar";

interface Chat {
  id: number;
  title: string;
}
interface Msg {
  role: "user" | "assistant";
  content: string;
}

const QUICK_PROMPTS: { label: string; prompt: string }[] = [
  { label: "College Outfit", prompt: "What should I wear to college tomorrow?" },
  { label: "Party Outfit", prompt: "Suggest an outfit for a birthday party." },
  { label: "Interview Outfit", prompt: "I need an outfit for a job interview." },
  { label: "Casual Outfit", prompt: "Suggest a comfy casual outfit for the weekend." },
  { label: "Travel Outfit", prompt: "What should I wear for a long travel day?" },
  { label: "Formal Outfit", prompt: "Help me put together a formal evening outfit." },
  { label: "Date/Function Outfit", prompt: "Suggest a stylish outfit for a dinner date." },
  { label: "Match My Clothes", prompt: "I have a black top and blue jeans. How can I style them?" },
];

// Renders **bold** and preserves line breaks.
function renderContent(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((p, i) =>
    p.startsWith("**") && p.endsWith("**") ? (
      <strong key={i}>{p.slice(2, -2)}</strong>
    ) : (
      <span key={i}>{p}</span>
    )
  );
}

export default function ChatPage() {
  const [chats, setChats] = useState<Chat[]>([]);
  const [activeId, setActiveId] = useState<number | null>(null);
  const [messages, setMessages] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const loadChats = useCallback(async () => {
    const res = await fetch("/api/chats");
    const data = await res.json();
    setChats(data.chats || []);
  }, []);

  const loadMessages = useCallback(async (id: number) => {
    const res = await fetch(`/api/chat?conversation_id=${id}`);
    const data = await res.json();
    setMessages(
      (data.messages || []).map((m: Msg) => ({
        role: m.role,
        content: m.content,
      }))
    );
  }, []);

  useEffect(() => {
    loadChats();
  }, [loadChats]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const selectChat = async (id: number) => {
    setActiveId(id);
    setSidebarOpen(false);
    await loadMessages(id);
  };

  const newChat = () => {
    setActiveId(null);
    setMessages([]);
    setSidebarOpen(false);
  };

  const deleteChat = async (id: number) => {
    await fetch(`/api/chats/${id}`, { method: "DELETE" });
    if (activeId === id) newChat();
    await loadChats();
  };

  const send = async (text: string) => {
    const message = text.trim();
    if (!message || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    setLoading(true);
    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ message, conversation_id: activeId }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Request failed");
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.reply },
      ]);
      if (!activeId && data.conversation_id) {
        setActiveId(data.conversation_id);
        loadChats();
      }
    } catch (e) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "⚠️ " +
            (e instanceof Error ? e.message : "Something went wrong.") +
            " Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const clearChat = () => setMessages([]);

  return (
    <div className="flex min-h-screen flex-col">
      <NavBar />
      <div className="mx-auto flex w-full max-w-6xl flex-1 gap-4 px-2 py-4 md:px-4">
        {/* Sidebar */}
        <aside
          className={`${
            sidebarOpen ? "fixed inset-0 z-50 block bg-black/40 md:static md:bg-transparent" : "hidden"
          } md:block md:w-64 md:shrink-0`}
          onClick={() => setSidebarOpen(false)}
        >
          <div
            className="flex h-full w-64 flex-col rounded-2xl border border-black/5 bg-white p-3 shadow-sm md:h-auto"
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={newChat}
              className="mb-3 rounded-xl bg-[#3b1d3a] px-4 py-2.5 text-sm font-semibold text-white transition hover:opacity-90"
            >
              + New Chat
            </button>
            <p className="px-1 pb-1 text-xs font-semibold uppercase text-[#241322]/40">
              Chat History
            </p>
            <div className="thin-scroll flex-1 space-y-1 overflow-y-auto md:max-h-[60vh]">
              {chats.length === 0 && (
                <p className="px-2 py-3 text-xs text-[#241322]/40">
                  No conversations yet.
                </p>
              )}
              {chats.map((c) => (
                <div
                  key={c.id}
                  className={`group flex items-center gap-1 rounded-lg px-2 py-2 text-sm transition ${
                    activeId === c.id
                      ? "bg-[#e0577d]/10 text-[#3b1d3a]"
                      : "hover:bg-black/5"
                  }`}
                >
                  <button
                    onClick={() => selectChat(c.id)}
                    className="flex-1 truncate text-left"
                    title={c.title}
                  >
                    💬 {c.title}
                  </button>
                  <button
                    onClick={() => deleteChat(c.id)}
                    className="opacity-0 transition group-hover:opacity-100"
                    title="Delete chat"
                  >
                    🗑️
                  </button>
                </div>
              ))}
            </div>
          </div>
        </aside>

        {/* Main chat */}
        <main className="flex flex-1 flex-col rounded-2xl border border-black/5 bg-white shadow-sm">
          <div className="flex items-center justify-between border-b border-black/5 px-4 py-3">
            <div className="flex items-center gap-2">
              <button
                onClick={() => setSidebarOpen(true)}
                className="rounded-lg border border-black/10 px-2 py-1 text-sm md:hidden"
              >
                ☰
              </button>
              <span className="grid h-8 w-8 place-items-center rounded-full bg-gradient-to-br from-[#e0577d] to-[#d8a24a]">
                👗
              </span>
              <div>
                <p className="text-sm font-bold text-[#3b1d3a]">StyleMate AI</p>
                <p className="text-xs text-[#241322]/50">
                  Your friendly fashion stylist
                </p>
              </div>
            </div>
            <button
              onClick={clearChat}
              className="rounded-full border border-black/10 px-3 py-1.5 text-xs font-semibold text-[#3b1d3a] transition hover:bg-black/5"
            >
              Clear
            </button>
          </div>

          {/* Messages */}
          <div className="thin-scroll flex-1 space-y-4 overflow-y-auto px-4 py-5 md:h-[52vh]">
            {messages.length === 0 && !loading && (
              <div className="mx-auto max-w-md pt-6 text-center">
                <div className="text-5xl">✨</div>
                <h2 className="mt-3 font-serif-display text-2xl font-bold text-[#3b1d3a]">
                  Hi! I&apos;m StyleMate AI
                </h2>
                <p className="mt-2 text-sm text-[#241322]/60">
                  Ask me anything about outfits, colors, or styling. Try a quick
                  prompt below to get started!
                </p>
              </div>
            )}
            {messages.map((m, i) => (
              <div
                key={i}
                className={`flex ${
                  m.role === "user" ? "justify-end" : "justify-start"
                }`}
              >
                <div
                  className={`chat-content max-w-[85%] rounded-2xl px-4 py-3 text-sm ${
                    m.role === "user"
                      ? "bg-[#3b1d3a] text-white"
                      : "bg-[#fbf7f2] text-[#241322]"
                  }`}
                >
                  {renderContent(m.content)}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-1 rounded-2xl bg-[#fbf7f2] px-4 py-3">
                  <span className="typing-dot h-2 w-2 rounded-full bg-[#e0577d]" />
                  <span
                    className="typing-dot h-2 w-2 rounded-full bg-[#e0577d]"
                    style={{ animationDelay: "0.2s" }}
                  />
                  <span
                    className="typing-dot h-2 w-2 rounded-full bg-[#e0577d]"
                    style={{ animationDelay: "0.4s" }}
                  />
                </div>
              </div>
            )}
            <div ref={endRef} />
          </div>

          {/* Quick prompts */}
          <div className="flex flex-wrap gap-2 border-t border-black/5 px-4 py-3">
            {QUICK_PROMPTS.map((q) => (
              <button
                key={q.label}
                onClick={() => send(q.prompt)}
                disabled={loading}
                className="rounded-full border border-[#e0577d]/30 bg-[#e0577d]/5 px-3 py-1.5 text-xs font-semibold text-[#e0577d] transition hover:bg-[#e0577d]/10 disabled:opacity-50"
              >
                {q.label}
              </button>
            ))}
          </div>

          {/* Composer */}
          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(input);
            }}
            className="flex items-end gap-2 border-t border-black/5 p-3"
          >
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  send(input);
                }
              }}
              rows={1}
              placeholder="Ask StyleMate anything… e.g. What colors go with beige pants?"
              className="max-h-32 flex-1 resize-none rounded-xl border border-black/10 px-4 py-3 text-sm outline-none focus:border-[#e0577d]"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="rounded-xl bg-[#e0577d] px-5 py-3 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-50"
            >
              Send
            </button>
          </form>
        </main>
      </div>
    </div>
  );
}
