"use client";

import { useRef, useState } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

type ChatMessage = {
  prompt: string;
  response: string;
  action: string;
};

type ChatApiResponse = {
  response: string | null;
  action: string;
  message: string;
  risk_score: number;
  trust_score: number;
  reauth_required: boolean;
};

export default function Chat() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const sendMessage = async () => {
    const nextPrompt = prompt.trim();
    if (!nextPrompt || loading) return;

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          user_id: "user1",
          prompt: nextPrompt
        })
      });

      const data = (await res.json()) as ChatApiResponse;
      if (!res.ok) {
        throw new Error(data.message || "Request failed");
      }

      setMessages((prev) => [
        ...prev,
        {
          prompt: nextPrompt,
          response: data.response ?? data.message,
          action: data.action
        }
      ]);

      setPrompt("");
    } catch (err) {
      console.error("Failed to send message:", err);
      setError(`Unable to reach the backend at ${API_BASE}.`);
    } finally {
      setLoading(false);

      if (textareaRef.current) {
        textareaRef.current.focus();
        textareaRef.current.style.height = "auto";
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && e.ctrlKey) {
      void sendMessage();
    }
  };

  const handleInput = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-6">
      <div className="mx-auto max-w-2xl">
        <h1 className="mb-8 text-3xl font-bold text-white">Secure Chat</h1>

        {error && (
          <div className="mb-4 rounded-lg border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-100">
            {error}
          </div>
        )}

        <div className="mb-6 h-96 overflow-y-auto rounded-lg border border-slate-700 bg-slate-950 p-4 shadow-2xl">
          {messages.length === 0 ? (
            <div className="flex h-full items-center justify-center text-slate-500">
              <p>No messages yet. Start a conversation!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, i) => (
                <div key={`${msg.prompt}-${i}`} className="space-y-2">
                  <div className="flex justify-end">
                    <div className="max-w-xs rounded-lg bg-blue-600 px-4 py-2 text-white">
                      <p className="text-sm">{msg.prompt}</p>
                    </div>
                  </div>
                  <div className="flex justify-start">
                    <div className="max-w-xs rounded-lg bg-slate-700 px-4 py-2 text-slate-100">
                      <p className="text-sm">{msg.response || msg.action}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="rounded-lg border border-slate-700 bg-slate-900 p-4 shadow-2xl">
          <div className="flex gap-3">
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onInput={handleInput}
                onKeyDown={handleKeyDown}
                disabled={loading}
                maxLength={500}
                placeholder="Type your message... (Ctrl+Enter to send)"
                className="max-h-32 w-full resize-none rounded-lg border border-slate-600 bg-slate-800 p-3 text-white placeholder-slate-500 transition focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20"
                rows={1}
              />
              <div className="mt-2 flex items-center justify-between px-1">
                <span className="text-xs text-slate-500">{prompt.length}/500 characters</span>
                <span className="text-xs text-slate-500">{loading && "Sending..."}</span>
              </div>
            </div>

            <button
              onClick={() => void sendMessage()}
              disabled={loading || !prompt.trim()}
              className="mt-1 h-fit self-start rounded-lg bg-blue-600 px-6 py-2 font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-700"
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
