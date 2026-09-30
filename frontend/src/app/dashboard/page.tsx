"use client";

import { useEffect, useState } from "react";
import { getDashboard, getPredictionHistory, logout } from "@/lib/api";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function DashboardPage() {
  const router = useRouter();
  const [data, setData] = useState<any>(null);
  const [history, setHistory] = useState<any[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    (async () => {
      try {
        const d = await getDashboard();
        setData(d);
        const h = await getPredictionHistory();
        setHistory(h);
      } catch (e: any) {
        setError("Please log in to view your dashboard.");
      }
    })();
  }, []);

  const handleLogout = () => {
    logout();
    router.push("/login");
  };

  if (error) {
    return (
      <div className="card-3d text-center space-y-4">
        <p className="text-slate-200">{error}</p>
        <Link href="/login" className="btn-primary inline-block">
          Go to Login
        </Link>
      </div>
    );
  }

  if (!data) {
    return <div className="text-slate-400">Loading dashboard…</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h2 className="text-2xl font-bold text-white">
            Hello{data.user.full_name ? `, ${data.user.full_name}` : ""}
          </h2>
          <p className="text-sm text-slate-400">
            {data.user.email} · Role: {data.user.role}
          </p>
        </div>
        <button className="btn-secondary text-sm" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <div className="grid sm:grid-cols-3 gap-4">
        {[
          { label: "Predictions", value: data.stats.predictions, href: "/predict" },
          { label: "Conversations", value: data.stats.conversations, href: "/chat" },
          { label: "Nutrition logs", value: data.stats.nutrition_logs, href: "/nutrition" },
        ].map((s) => (
          <Link key={s.label} href={s.href} className="card-3d hover:shadow-md transition-shadow text-center">
            <p className="text-3xl font-bold text-primary-700">{s.value}</p>
            <p className="text-sm text-slate-400 mt-1">{s.label}</p>
          </Link>
        ))}
      </div>

      <div className="card-3d">
        <h3 className="font-semibold text-lg mb-3">Recent predictions</h3>
        {history.length === 0 ? (
          <p className="text-sm text-slate-400">No predictions yet. Try the Predict page.</p>
        ) : (
          <ul className="divide-y divide-slate-100">
            {history.map((h) => (
              <li key={h.id} className="py-3 flex justify-between gap-4 text-sm">
                <div>
                  <p className="font-medium text-white">{h.top_disease || "—"}</p>
                  <p className="text-slate-400 text-xs mt-0.5">
                    Symptoms: {(h.symptoms || []).join(", ")}
                  </p>
                </div>
                <div className="text-right shrink-0">
                  <p className="font-medium text-primary-700">
                    {h.top_confidence != null ? `${(h.top_confidence * 100).toFixed(0)}%` : "—"}
                  </p>
                  <p className="text-xs text-slate-400">
                    {h.created_at ? new Date(h.created_at).toLocaleString() : ""}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="flex flex-wrap gap-3">
        <Link href="/predict" className="btn-primary">New prediction</Link>
        <Link href="/chat" className="btn-secondary">Open chatbot</Link>
        <Link href="/nutrition" className="btn-secondary">Nutrition calc</Link>
      </div>
    </div>
  );
}
