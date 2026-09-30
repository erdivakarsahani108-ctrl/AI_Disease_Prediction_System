"use client";

import { useState, useRef, useEffect } from "react";
import { sendChat, ChatResponse } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  meta?: Partial<ChatResponse>;
}

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Namaste! Main aapka educational medical assistant hoon.\nEnglish, Hindi, Hinglish ya Bhojpuri mein pooch sakte ho.\nSymptoms batao ya koi health question poocho.\n\n⚠️ Main diagnosis nahi karta — doctor se salah lein.",
    },
  ]);
  const [input, setInput] = useState("");
  const [mode, setMode] = useState("patient");
  const [system, setSystem] = useState("");
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const send = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", content: text }]);
    setLoading(true);
    try {
      const res = await sendChat(text, mode, system || undefined);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: res.reply,
          meta: res,
        },
      ]);
    } catch (e: any) {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: "Sorry, something went wrong. Please try again.\n" + (e.message || ""),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-12rem)] max-h-[800px]">
      <div className="mb-4">
        <h2 className="text-2xl font-bold text-white">Medical Chatbot</h2>
        <p className="text-slate-400 text-sm mt-1">
          Multilingual • Safety-gated • Educational only
        </p>
      </div>

      <div className="flex flex-wrap gap-3 mb-3">
        <select className="input max-w-[160px] py-2 text-sm" value={mode} onChange={(e) => setMode(e.target.value)}>
          <option value="patient">Patient mode</option>
          <option value="student">Student mode</option>
          <option value="clinician">Clinician mode</option>
        </select>
        <select className="input max-w-[200px] py-2 text-sm" value={system} onChange={(e) => setSystem(e.target.value)}>
          <option value="">Any medical system</option>
          <option value="allopathy">Allopathy</option>
          <option value="ayurveda">Ayurveda</option>
          <option value="homeopathy">Homeopathy</option>
          <option value="unani">Unani</option>
          <option value="yoga_naturopathy">Yoga & Naturopathy</option>
          <option value="physiotherapy">Physiotherapy</option>
        </select>
      </div>

      <div className="flex-1 overflow-y-auto card space-y-4 mb-4">
        {messages.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "bubble-user"
                  : "bg-slate-100 text-slate-100 rounded-bl-md"
              }`}
            >
              {msg.content}
              {msg.meta?.language_name && (
                <div className="mt-2 pt-2 border-t border-white/10 text-xs text-slate-400">
                  Detected: {msg.meta.language_name}
                  {msg.meta.safety?.risk_level &&
                    ` • Risk: ${msg.meta.safety.risk_level}`}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-100 rounded-2xl px-4 py-3 text-sm text-slate-400">
              Thinking…
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      <div className="flex gap-2">
        <input
          className="input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type in English, Hindi, Hinglish or Bhojpuri…"
          onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && send()}
          disabled={loading}
        />
        <button className="btn-primary shrink-0" onClick={send} disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}
