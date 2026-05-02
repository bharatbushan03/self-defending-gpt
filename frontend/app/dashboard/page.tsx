"use client";

import { useEffect, useState } from "react";

export default function Dashboard() {
  const [logs, setLogs] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/logs")
      .then((res) => res.json())
      .then((data) => setLogs(data));
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Security Dashboard</h1>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th>Prompt</th>
            <th>Label</th>
            <th>Risk</th>
            <th>Action</th>
            <th>Time</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log: any, index: number) => (
            <tr key={index} className="border">
              <td>{log.prompt}</td>
              <td>{log.label}</td>
              <td>{log.risk_score}</td>

              <td
                className={
                  log.action === "BLOCK"
                    ? "text-red-600 font-bold"
                    : log.action === "WARN"
                    ? "text-yellow-600"
                    : "text-green-600"
                }
              >
                {log.action}
              </td>

              <td>{new Date(log.timestamp).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}