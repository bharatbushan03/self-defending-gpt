"use client";

import { useEffect, useMemo, useState } from "react";
import {
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis
} from "recharts";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";
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
    if (!API_BASE) {
      setError("NEXT_PUBLIC_API_URL is not configured.");
      setLogs([]);
      return;
    }

    fetch(`${API_BASE}/logs`)
      .then((res) => res.json())
      .then((data: unknown) => {
        setLogs(Array.isArray(data) ? (data as LogEntry[]) : []);
        setError(null);
      })
      .catch((err) => {
        console.error("Failed to fetch logs:", err);
        setError("Cannot connect to backend. Check NEXT_PUBLIC_API_URL.");
        setLogs([]);
      });
  }, []);

  useEffect(() => {
    if (!API_BASE) {
      setChartData([]);
      setTrendData([]);
      setUsers([]);
      return;
    }

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
  const blocked = logs.filter((log) => log.action === "BLOCK").length;
  const warned = logs.filter((log) => log.action === "WARN").length;
  const allowed = logs.filter((log) => log.action === "ALLOW").length;
  const totalEvents = logs.length;

  const latestAttacks = useMemo(() => logs.slice(0, 8), [logs]);
  const fallbackChartData = [
    { name: "Safe", value: safe },
    { name: "Suspicious", value: suspicious },
    { name: "Malicious", value: malicious }
  ];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-8 px-4 py-8 sm:px-6 lg:px-8">
        <header className="flex flex-col gap-4 border-b border-slate-800 pb-6">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.3em] text-emerald-400">
                Security Operations Center
              </p>
              <h1 className="text-3xl font-semibold text-white sm:text-4xl">Threat Intelligence</h1>
            </div>
            <div className="rounded-full border border-slate-800 bg-slate-900 px-4 py-2 text-xs text-slate-300">
              Live feed: {API_BASE ? API_BASE.replace(/^https?:\/\//, "") : "Not configured"}
            </div>
          </div>
          <p className="max-w-3xl text-sm text-slate-400">
            Monitor risk posture, containment actions, and attacker behavior from the unified telemetry
            stream.
          </p>
        </header>

        {error && (
          <div className="rounded-lg border border-rose-500/40 bg-rose-500/10 p-4 text-sm text-rose-200">
            Warning: {error}
          </div>
        )}

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <div className="rounded-2xl border border-emerald-500/30 bg-gradient-to-br from-emerald-500/20 via-slate-900 to-slate-950 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-emerald-200">Total Events</p>
            <p className="mt-4 text-3xl font-semibold text-white">{totalEvents}</p>
            <p className="mt-2 text-xs text-slate-400">Across all ingested prompts</p>
          </div>
          <div className="rounded-2xl border border-rose-500/30 bg-gradient-to-br from-rose-500/20 via-slate-900 to-slate-950 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-rose-200">Blocked Attacks</p>
            <p className="mt-4 text-3xl font-semibold text-white">{blocked}</p>
            <p className="mt-2 text-xs text-slate-400">Immediate containment actions</p>
          </div>
          <div className="rounded-2xl border border-amber-500/30 bg-gradient-to-br from-amber-500/20 via-slate-900 to-slate-950 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-amber-200">Investigations</p>
            <p className="mt-4 text-3xl font-semibold text-white">{warned}</p>
            <p className="mt-2 text-xs text-slate-400">Threats awaiting triage</p>
          </div>
          <div className="rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-cyan-500/20 via-slate-900 to-slate-950 p-5">
            <p className="text-xs uppercase tracking-[0.2em] text-cyan-200">Allowed Sessions</p>
            <p className="mt-4 text-3xl font-semibold text-white">{allowed}</p>
            <p className="mt-2 text-xs text-slate-400">Cleared by policy engine</p>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.1fr_1.4fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">Risk Distribution</h2>
                <p className="text-xs text-slate-400">Classification mix for the last ingest window</p>
              </div>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                Total: {totalEvents}
              </span>
            </div>
            <div className="mt-6 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={chartData.length ? chartData : fallbackChartData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={55}
                    outerRadius={90}
                    paddingAngle={3}
                  >
                    {(chartData.length ? chartData : fallbackChartData).map((_, index) => (
                      <Cell key={index} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                      color: "#e2e8f0"
                    }}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-6 grid grid-cols-3 gap-3 text-xs text-slate-400">
              <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-3">
                <p className="text-slate-300">Safe</p>
                <p className="mt-2 text-lg font-semibold text-emerald-300">
                  {chartData[0]?.value ?? safe}
                </p>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-3">
                <p className="text-slate-300">Suspicious</p>
                <p className="mt-2 text-lg font-semibold text-amber-300">
                  {chartData[1]?.value ?? suspicious}
                </p>
              </div>
              <div className="rounded-lg border border-slate-800 bg-slate-950/40 p-3">
                <p className="text-slate-300">Malicious</p>
                <p className="mt-2 text-lg font-semibold text-rose-300">
                  {chartData[2]?.value ?? malicious}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">Attack Trends</h2>
                <p className="text-xs text-slate-400">Daily drift for detected attacks</p>
              </div>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                Last 14 days
              </span>
            </div>
            <div className="mt-6 h-64">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={trendData} margin={{ top: 8, right: 16, bottom: 0, left: -8 }}>
                  <CartesianGrid stroke="#1e293b" strokeDasharray="4 4" />
                  <XAxis dataKey="date" stroke="#94a3b8" tick={{ fontSize: 12 }} />
                  <YAxis stroke="#94a3b8" tick={{ fontSize: 12 }} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: "#0f172a",
                      border: "1px solid #334155",
                      borderRadius: "8px",
                      color: "#e2e8f0"
                    }}
                  />
                  <Legend iconType="circle" />
                  <Line type="monotone" dataKey="Malicious" stroke="#fb7185" strokeWidth={2} />
                  <Line type="monotone" dataKey="Suspicious" stroke="#fbbf24" strokeWidth={2} />
                  <Line type="monotone" dataKey="Safe" stroke="#34d399" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1fr_1.3fr]">
          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">Top Risky Users</h2>
                <p className="text-xs text-slate-400">Highest cumulative risk scores</p>
              </div>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                Users: {users.length}
              </span>
            </div>
            <div className="mt-5 overflow-hidden rounded-xl border border-slate-800">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950/70 text-xs uppercase tracking-wider text-slate-400">
                  <tr>
                    <th className="px-4 py-3">User</th>
                    <th className="px-4 py-3 text-right">Total Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((user, index) => (
                    <tr key={`${user.user}-${index}`} className="border-t border-slate-800">
                      <td className="px-4 py-3 text-slate-100">{user.user}</td>
                      <td className="px-4 py-3 text-right font-semibold text-rose-200">
                        {user.score}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900/60 p-6">
            <div className="flex items-center justify-between">
              <div>
                <h2 className="text-lg font-semibold text-white">Recent Attacks</h2>
                <p className="text-xs text-slate-400">Latest suspicious or malicious prompts</p>
              </div>
              <span className="rounded-full bg-slate-800 px-3 py-1 text-xs text-slate-300">
                Showing {latestAttacks.length}
              </span>
            </div>
            <div className="mt-5 overflow-hidden rounded-xl border border-slate-800">
              <table className="w-full text-left text-sm">
                <thead className="bg-slate-950/70 text-xs uppercase tracking-wider text-slate-400">
                  <tr>
                    <th className="px-4 py-3">Prompt</th>
                    <th className="px-4 py-3">Label</th>
                    <th className="px-4 py-3">Risk</th>
                    <th className="px-4 py-3">Action</th>
                    <th className="px-4 py-3">Time</th>
                  </tr>
                </thead>
                <tbody>
                  {latestAttacks.map((log, index) => (
                    <tr key={`${log.prompt}-${index}`} className="border-t border-slate-800">
                      <td className="max-w-xs truncate px-4 py-3 text-slate-100">{log.prompt}</td>
                      <td className="px-4 py-3 text-slate-200">{log.label}</td>
                      <td className="px-4 py-3 text-slate-200">{log.risk_score}</td>
                      <td
                        className={
                          log.action === "BLOCK"
                            ? "px-4 py-3 font-semibold text-rose-300"
                            : log.action === "WARN"
                              ? "px-4 py-3 text-amber-300"
                              : "px-4 py-3 text-emerald-300"
                        }
                      >
                        {log.action}
                      </td>
                      <td className="px-4 py-3 text-slate-300">
                        {formatTimestamp(log.timestamp)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
