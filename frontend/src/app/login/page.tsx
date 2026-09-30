"use client";

import { useState } from "react";
import { login, register } from "@/lib/api";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [isRegister, setIsRegister] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [fullName, setFullName] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      if (isRegister) {
        await register(email, password, fullName || undefined);
      }
      await login(email, password);
      router.push("/dashboard");
    } catch (err: any) {
      setError(err?.response?.data?.detail || err.message || "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-md mx-auto">
      <div className="card-3d space-y-5">
        <h2 className="text-2xl font-bold text-white">
          {isRegister ? "Create account" : "Sign in"}
        </h2>
        <p className="text-sm text-slate-400">
          Persistent accounts store prediction history, nutrition logs and chat.
        </p>
        <form onSubmit={submit} className="space-y-4">
          {isRegister && (
            <div>
              <label className="block text-sm font-medium mb-1">Full name</label>
              <input className="input" value={fullName} onChange={(e) => setFullName(e.target.value)} />
            </div>
          )}
          <div>
            <label className="block text-sm font-medium mb-1">Email</label>
            <input
              className="input"
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Password (min 8)</label>
            <input
              className="input"
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>
          {error && (
            <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
              {error}
            </div>
          )}
          <button type="submit" className="btn-primary w-full" disabled={loading}>
            {loading ? "Please wait…" : isRegister ? "Register & Sign in" : "Sign in"}
          </button>
        </form>
        <button
          type="button"
          className="text-sm text-primary-600 hover:underline"
          onClick={() => setIsRegister(!isRegister)}
        >
          {isRegister ? "Already have an account? Sign in" : "Need an account? Register"}
        </button>
      </div>
    </div>
  );
}
