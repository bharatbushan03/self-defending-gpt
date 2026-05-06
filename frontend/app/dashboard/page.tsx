"use client";

import { useEffect, useState } from "react";
import {
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";
const COLORS = ["#00C49F", "#FFBB28", "#FF4C4C"] as const;

type LogEntry = {
  prompt: string;
  label: string;
  risk_score: number;
  action: string;
  timestamp?: string;
};

type ChartDatum = {
  name: "Safe" | "Suspicious" | "Malicious";
  value: number;
};

type TrendDatum = {
  date: string;
  Safe: number;
  Suspicious: number;
  Malicious: number;
};

type TopUser = {
  user: string;
  score: number;
};

const normalizeLabel = (value: unknown) => {
  if (typeof value !== "string") return "";
  return value.trim().toLowerCase();
};

const normalizeTopUser = (value: unknown): TopUser | null => {
  if (Array.isArray(value) && typeof value[0] === "string" && typeof value[1] === "number") {
    return { user: value[0], score: value[1] };
  }

  if (
    value &&
    typeof value === "object" &&
    "user" in value &&
    "score" in value &&
    typeof value.user === "string" &&
    typeof value.score === "number"
  ) {
    return { user: value.user, score: value.score };
  }

  return null;
};

const formatTimestamp = (value?: string) => {
  if (!value) return "-";

  const timestamp = new Date(value);
  if (Number.isNaN(timestamp.getTime())) {
    return value;
  }

  return timestamp.toLocaleString();
};

export default function Dashboard() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [chartData, setChartData] = useState<ChartDatum[]>([]);
  const [trendData, setTrendData] = useState<TrendDatum[]>([]);
  const [users, setUsers] = useState<TopUser[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch(`${API_BASE}/logs`)
      .then((res) => res.json())
      .then((data: unknown) => {
        setLogs(Array.isArray(data) ? (data as LogEntry[]) : []);
        setError(null);
      })
      .catch((err) => {
        console.error("Failed to fetch logs:", err);
        setError(`Cannot connect to backend at ${API_BASE}`);
        setLogs([]);
      });
  }, []);

  useEffect(() => {
    fetch(`${API_BASE}/analytics/risk-distribution`)
      .then((res) => res.json())
      .then((data: Record<string, number>) => {
        setChartData([
          { name: "Safe", value: data.Safe ?? data.safe ?? 0 },
          { name: "Suspicious", value: data.Suspicious ?? data.suspicious ?? 0 },
          { name: "Malicious", value: data.Malicious ?? data.malicious ?? 0 }
        ]);
      })
      .catch((err) => {
        console.error("Failed to fetch risk distribution:", err);
        setChartData([]);
      });

    fetch(`${API_BASE}/analytics/attack-trends`)
      .then((res) => res.json())
      .then((data: Record<string, unknown>) => {
        const rows: TrendDatum[] = Object.entries(data || {}).map(([date, counts]) => {
          const summary = counts as Record<string, number>;
          return {
            date,
            Safe: summary.Safe ?? summary.safe ?? 0,
            Suspicious: summary.Suspicious ?? summary.suspicious ?? 0,
            Malicious: summary.Malicious ?? summary.malicious ?? 0
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
      .then((res) => res.json())
      .then((data: unknown) => {
        const normalizedUsers = Array.isArray(data)
          ? data.map(normalizeTopUser).filter((user): user is TopUser => user !== null)
          : [];

        setUsers(normalizedUsers);
      })
      .catch((err) => {
        console.error("Failed to fetch top users:", err);
        setUsers([]);
      });
  }, []);

  const safe = logs.filter((log) => normalizeLabel(log.label) === "safe").length;
  const suspicious = logs.filter((log) => normalizeLabel(log.label) === "suspicious").length;
  const malicious = logs.filter((log) => normalizeLabel(log.label) === "malicious").length;

  return (
    <div className="space-y-8 p-6">
      <h1 className="text-2xl font-bold">Security Dashboard</h1>

      {error && (
        <div className="rounded border border-red-300 bg-red-100 p-4 text-red-700">
          Warning: {error}. Make sure the backend API is running on {API_BASE}.
        </div>
      )}

      <div className="grid grid-cols-3 gap-4">
        <div className="rounded bg-green-100 p-4">Safe: {chartData[0]?.value ?? safe}</div>
        <div className="rounded bg-yellow-100 p-4">
          Suspicious: {chartData[1]?.value ?? suspicious}
        </div>
        <div className="rounded bg-red-100 p-4">Malicious: {chartData[2]?.value ?? malicious}</div>
      </div>

      <div className="flex flex-wrap justify-center gap-8">
        <PieChart width={300} height={300}>
          <Pie
            data={
              chartData.length
                ? chartData
                : [
                    { name: "Safe", value: safe },
                    { name: "Suspicious", value: suspicious },
                    { name: "Malicious", value: malicious }
                  ]
            }
            dataKey="value"
            nameKey="name"
            outerRadius={100}
          >
            {(chartData.length ? chartData : [1, 2, 3]).map((_, index) => (
              <Cell key={index} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
        </PieChart>

        <LineChart width={500} height={300} data={trendData}>
          <XAxis dataKey="date" />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="Malicious" />
          <Line type="monotone" dataKey="Suspicious" />
          <Line type="monotone" dataKey="Safe" />
        </LineChart>
      </div>

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
            <tr key={`${log.prompt}-${index}`} className="border">
              <td>{log.prompt}</td>
              <td>{log.label}</td>
              <td>{log.risk_score}</td>
              <td
                className={
                  log.action === "BLOCK"
                    ? "font-bold text-red-600"
                    : log.action === "WARN"
                      ? "text-yellow-600"
                      : "text-green-600"
                }
              >
                {log.action}
              </td>
              <td>{formatTimestamp(log.timestamp)}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <table className="w-full border">
        <thead>
          <tr className="bg-gray-200">
            <th>User</th>
            <th>Total Risk Score</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user, index) => (
            <tr key={`${user.user}-${index}`} className="border">
              <td>{user.user}</td>
              <td>{user.score}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
