"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";

declare global {
  interface Window {
    webkitSpeechRecognition?: any;
    SpeechRecognition?: any;
  }
}

export default function VoiceScanPage() {
  const [consent, setConsent] = useState(false);
  const [listening, setListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [interim, setInterim] = useState("");
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState("");
  const [supported, setSupported] = useState(true);
  const [mode, setMode] = useState("patient");
  const [loading, setLoading] = useState(false);
  const recognitionRef = useRef<any>(null);
  const startTime = useRef<number>(0);

  useEffect(() => {
    const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SR) {
      setSupported(false);
      return;
    }
    const rec = new SR();
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = "en-IN"; // works well for Indian English / Hinglish mix
    rec.onresult = (event: any) => {
      let finalText = "";
      let interimText = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const t = event.results[i][0].transcript;
        if (event.results[i].isFinal) finalText += t;
        else interimText += t;
      }
      if (finalText) setTranscript((prev) => (prev + " " + finalText).trim());
      setInterim(interimText);
    };
    rec.onerror = (e: any) => {
      setError(e.error || "Speech recognition error");
      setListening(false);
    };
    rec.onend = () => setListening(false);
    recognitionRef.current = rec;
  }, []);

  const toggleListen = () => {
    if (!consent) {
      setError("Please accept microphone consent first.");
      return;
    }
    if (!recognitionRef.current) return;
    setError("");
    if (listening) {
      recognitionRef.current.stop();
      setListening(false);
    } else {
      setResult(null);
      startTime.current = Date.now();
      try {
        recognitionRef.current.start();
        setListening(true);
      } catch {
        setError("Could not start microphone. Check browser permissions.");
      }
    }
  };

  const analyze = async () => {
    const text = (transcript + " " + interim).trim();
    if (!text) {
      setError("No speech captured yet.");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const duration_sec = (Date.now() - startTime.current) / 1000;
      const { data } = await api.post("/voice/scan", {
        transcript: text,
        mode,
        consent_given: consent,
        audio_quality: {
          duration_sec,
          noise_level: 0.3,
          source: "web_speech_api",
        },
      });
      setResult(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || "Scan failed");
    } finally {
      setLoading(false);
    }
  };

  const onImageDesc = async (description: string, modality: string) => {
    if (!consent) {
      setError("Consent required.");
      return;
    }
    setLoading(true);
    try {
      const { data } = await api.post("/multimodal/scan", {
        description,
        modality,
        consent_given: consent,
        mode,
        quality: { blur: 0.2, lighting: 0.8 },
      });
      setResult(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white hero-glow">Voice & Multimodal Scan</h2>
        <p className="text-slate-400 mt-1 text-sm">
          Speak symptoms in English / Hinglish. Browser speech → text → safety + prediction pipeline.
          Not acoustic medical diagnosis.
        </p>
      </div>

      {/* Consent */}
      <div className="card-3d border border-cyan-500/20">
        <label className="flex items-start gap-3 cursor-pointer">
          <input
            type="checkbox"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            className="mt-1 w-4 h-4"
          />
          <span className="text-sm text-slate-300">
            <strong className="text-cyan-300">Consent:</strong> I allow microphone access for
            educational symptom capture. Audio is processed in-browser to text; I understand this is
            not a medical diagnosis and not stored as raw clinical audio by default.
          </span>
        </label>
      </div>

      {!supported && (
        <div className="card-3d text-amber-300 text-sm">
          Web Speech API not supported in this browser. Use Chrome/Edge, or type symptoms on the
          Predict page.
        </div>
      )}

      <div className="card-3d space-y-4">
        <div className="flex flex-wrap gap-3 items-center">
          <select className="input max-w-[140px]" value={mode} onChange={(e) => setMode(e.target.value)}>
            <option value="patient">Patient</option>
            <option value="student">Student</option>
            <option value="clinician">Clinician</option>
          </select>
          <button
            type="button"
            className={`btn-primary min-w-[140px] ${listening ? "animate-pulse" : ""}`}
            onClick={toggleListen}
            disabled={!supported}
          >
            {listening ? "● Stop" : "🎤 Start mic"}
          </button>
          <button type="button" className="btn-secondary" onClick={analyze} disabled={loading || !transcript}>
            {loading ? "Analyzing…" : "Analyze transcript"}
          </button>
          <button
            type="button"
            className="btn-secondary text-sm"
            onClick={() => {
              setTranscript("");
              setInterim("");
              setResult(null);
            }}
          >
            Clear
          </button>
        </div>

        <div className="rounded-xl bg-black/40 border border-white/10 p-4 min-h-[100px]">
          <p className="text-xs text-slate-500 mb-1">Transcript</p>
          <p className="text-white whitespace-pre-wrap">
            {transcript || <span className="text-slate-600">Speak after granting consent…</span>}
            {interim && <span className="text-cyan-400/70"> {interim}</span>}
          </p>
        </div>

        <div>
          <p className="text-xs text-slate-500 mb-2">Or describe an image (no CV diagnosis in this build)</p>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              className="btn-secondary text-sm"
              onClick={() =>
                onImageDesc(
                  prompt("Describe what you see (skin/rash/document) or cancel:") || "",
                  "skin_image"
                )
              }
            >
              📷 Skin note
            </button>
            <button
              type="button"
              className="btn-secondary text-sm"
              onClick={() =>
                onImageDesc(prompt("Describe the document/label text:") || "", "document")
              }
            >
              📄 Document note
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="text-sm text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-2">
          {error}
        </div>
      )}

      {result && (
        <div className="card-3d space-y-3">
          {result.emergency && (
            <p className="text-red-400 font-semibold">🚨 {result.reply || result.disclaimer}</p>
          )}
          {result.quality_notes?.length > 0 && (
            <ul className="text-amber-300/90 text-sm list-disc list-inside">
              {result.quality_notes.map((n: string, i: number) => (
                <li key={i}>{n}</li>
              ))}
            </ul>
          )}
          {result.detected_symptoms?.length > 0 && (
            <p className="text-sm text-slate-300">
              Symptoms: <span className="text-cyan-300">{result.detected_symptoms.join(", ")}</span>
            </p>
          )}
          {result.predictions?.length > 0 && (
            <ul className="space-y-2">
              {result.predictions.map((p: any) => (
                <li key={p.disease} className="flex justify-between border-b border-white/5 pb-2 text-sm">
                  <span className="text-white">{p.disease}</span>
                  <span className="text-cyan-400">{(p.confidence * 100).toFixed(0)}%</span>
                </li>
              ))}
            </ul>
          )}
          {result.reply && !result.emergency && (
            <p className="text-sm text-slate-300 whitespace-pre-wrap border-t border-white/10 pt-3">
              {result.reply}
            </p>
          )}
          <p className="text-xs text-slate-500 italic">{result.disclaimer}</p>
        </div>
      )}
    </div>
  );
}

