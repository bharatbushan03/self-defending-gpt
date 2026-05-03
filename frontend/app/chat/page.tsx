"use client";

import { useState } from "react";

export default function Chat() {
  const [prompt, setPrompt] = useState("");
  const [messages, setMessages] = useState<any[]>([]);

  const sendMessage = async () => {
    if (!prompt.trim()) return;

    const res = await fetch("http://127.0.0.1:8000/chat", {
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
  };

  return (
    <div className="p-6 max-w-xl mx-auto">
      <h1 className="text-xl font-bold mb-4">Secure Chat</h1>

      <div className="flex gap-2">
        <input
          className="border p-2 w-full rounded"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Type your message..."
        />

        <button
          onClick={sendMessage}
          className="bg-blue-500 text-white px-4 rounded"
        >
          Send
        </button>
      </div>

      <div className="mt-6">
        {messages.map((msg, i) => (
          <div key={i} className="mb-4 p-3 border rounded bg-gray-50">
            <p className="text-blue-600">
              <b>You:</b> {msg.prompt}
            </p>
            <p className="text-green-600">
              <b>Bot:</b> {msg.response || msg.action}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}