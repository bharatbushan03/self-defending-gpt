"use client";

import { useEffect, useState } from "react";
import {
  PieChart, Pie, Cell, Tooltip,
  LineChart, Line, XAxis, YAxis
} from "recharts";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const COLORS = ["#00C49F", "#FFBB28", "#FF4C4C"];

const normalizeLabel = (value: unknown) => {
  if (typeof value !== "string") return "";
  return value.trim().toLowerCase();
};

export default function Dashboard() {
  const [logs, setLogs] = useState<any[]>([]);
  const [chartData, setChartData] = useState<any[]>([]);
  const [trendData, setTrendData] = useState<any[]>([]);
  const [users, setUsers] = useState<any[]>([]);

  const [error, setError] = useState<string | null>(null);

  // ✅ Fetch raw logs
  useEffect(() => {
    fetch(`${API_BASE}/logs`)
      .then(res => res.json())
      .then((data) => {
        setLogs(Array.isArray(data) ? data : []);
        setError(null);
      })
      .catch((err) => {
        console.error("Failed to fetch logs:", err);
        setError(`Cannot connect to backend at ${API_BASE}`);
        setLogs([]);
      });
  }, []);

  // ✅ Fetch analytics APIs (clean separation)
  useEffect(() => {
    fetch(`${API_BASE}/analytics/risk-distribution`)
      .then(res => res.json())
      .then((data) => {
        setChartData([
          { name: "Safe", value: data.Safe ?? data.safe ?? 0 },
          { name: "Suspicious", value: data.Suspicious ?? data.suspicious ?? 0 },
          { name: "Malicious", value: data.Malicious ?? data.malicious ?? 0 },
        ]);
      })
      .catch((err) => {
        console.error("Failed to fetch risk distribution:", err);
        setChartData([]);
      });

    fetch(`${API_BASE}/analytics/attack-trends`)
      .then(res => res.json())
      .then((data) => {
        const rows = Object.entries(data || {}).map(([date, counts]) => {
          const summary = counts as Record<string, number>;
          return {
            date,
            Safe: summary.Safe ?? summary.safe ?? 0,
            Suspicious: summary.Suspicious ?? summary.suspicious ?? 0,
            Malicious: summary.Malicious ?? summary.malicious ?? 0,
          };
        });
        rows.sort((a, b) => a.date.localeCompare(b.date));
        setTrendData(rows);
      })
      .catch((err) => {
        console.error("Failed to fetch attack trends:", err);
        setTrendData([]);
      });

    fetch(`${API_BASE}/analytics/top-users`)
      .then(res => res.json())
      .then((data) => setUsers(Array.isArray(data) ? data : []))
      .catch((err) => {
        console.error("Failed to fetch top users:", err);
        setUsers([]);
      });
  }, []);

  // ✅ Fallback counts (if analytics fails)
  const safe = logs.filter(l => normalizeLabel(l.label) === "safe").length;
  const suspicious = logs.filter(l => normalizeLabel(l.label) === "suspicious").length;
  const malicious = logs.filter(l => normalizeLabel(l.label) === "malicious").length;

  return (
    <div className="p-6 space-y-8">
      <h1 className="text-2xl font-bold">Security Dashboard</h1>

      {error && (
        <div className="p-4 bg-red-100 text-red-700 rounded border border-red-300">
          ⚠️ {error}. Make sure the backend API is running on {API_BASE}.
        </div>
      )}

      {/* ✅ Summary Cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-green-100 rounded">
          Safe: {chartData[0]?.value ?? safe}
        </div>
        <div className="p-4 bg-yellow-100 rounded">
          Suspicious: {chartData[1]?.value ?? suspicious}
        </div>
        <div className="p-4 bg-red-100 rounded">
          Malicious: {chartData[2]?.value ?? malicious}
        </div>
      </div>

      {/* ✅ Charts */}
      <div className="flex flex-wrap gap-8 justify-center">
        {/* Pie Chart */}
        <PieChart width={300} height={300}>
          <Pie
            data={chartData.length ? chartData : [
              { name: "Safe", value: safe },
              { name: "Suspicious", value: suspicious },
              { name: "Malicious", value: malicious },
            ]}
            dataKey="value"
            nameKey="name"
            outerRadius={100}
          >
            {(chartData.length ? chartData : [1,2,3]).map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>

        {/* Line Chart */}
        <LineChart width={500} height={300} data={trendData}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="Malicious" />
          <Line type="monotone" dataKey="Suspicious" />
          <Line type="monotone" dataKey="Safe" />
        </LineChart>
      </div>

      {/* ✅ Logs Table */}
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
          {logs.map((log, index) => (
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

      {/* ✅ User Risk Table */}
      <table className="w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th>User</th>
            <th>Total Risk Score</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u: any, i: number) => (
            <tr key={i} className="border">
              <td>{u.user || u[0]}</td>
              <td>{u.score || u[1]}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}