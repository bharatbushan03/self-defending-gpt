"use client";

import { useState, useRef, useEffect } from "react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export default function Chat() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const sendMessage = async () => {
    if (!prompt.trim()) return;

    setLoading(true);

    const res = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        user_id: "user1",
        prompt
      })
    });

    const data = await res.json();

    setMessages((prev) => [
      ...prev,
      {
        prompt,
        response: data.response,
        action: data.action
      }
    ]);

    setPrompt("");
    setLoading(false);

    if (textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.style.height = "auto";
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && e.ctrlKey) {
      sendMessage();
    }
  };

  const handleInput = () => {
    if (textareaRef.current) {
      textareaRef.current.style.height = "auto";
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 150) + "px";
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 to-slate-800 p-6">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-white">🔒 Secure Chat</h1>

        {/* Chat Messages */}
        <div className="bg-slate-950 rounded-lg shadow-2xl p-4 mb-6 h-96 overflow-y-auto border border-slate-700">
          {messages.length === 0 ? (
            <div className="flex items-center justify-center h-full text-slate-500">
              <p>No messages yet. Start a conversation!</p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((msg, i) => (
                <div key={i} className="space-y-2">
                  <div className="flex justify-end">
                    <div className="bg-blue-600 text-white rounded-lg px-4 py-2 max-w-xs">
                      <p className="text-sm">{msg.prompt}</p>
                    </div>
                  </div>
                  <div className="flex justify-start">
                    <div className="bg-slate-700 text-slate-100 rounded-lg px-4 py-2 max-w-xs">
                      <p className="text-sm">{msg.response || msg.action}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="bg-slate-900 rounded-lg shadow-2xl p-4 border border-slate-700">
          <div className="flex gap-3">
            <div className="flex-1">
              <textarea
                ref={textareaRef}
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onInput={handleInput}
                onKeyDown={handleKeyDown}
                disabled={loading}
                placeholder="Type your message... (Ctrl+Enter to send)"
                className="w-full p-3 rounded-lg bg-slate-800 text-white placeholder-slate-500 border border-slate-600 focus:border-blue-500 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition resize-none max-h-32"
                rows={1}
              />
              <div className="flex justify-between items-center mt-2 px-1">
                <span className="text-xs text-slate-500">
                  {prompt.length}/500 characters
                </span>
                <span className="text-xs text-slate-500">
                  {loading && "Sending..."}
                </span>
              </div>
            </div>

            <button
              onClick={sendMessage}
              disabled={loading || !prompt.trim()}
              className="bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed text-white px-6 py-2 rounded-lg font-semibold transition h-fit self-start mt-1"
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}