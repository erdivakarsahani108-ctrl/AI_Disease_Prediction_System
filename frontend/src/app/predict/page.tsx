"use client";

import { useState } from "react";
import { predictDiseases, PredictResponse } from "@/lib/api";

const COMMON_SYMPTOMS = [
  "fever", "cough", "fatigue", "headache", "sore_throat", "runny_nose",
  "body_ache", "chills", "nausea", "vomiting", "diarrhea", "abdominal_pain",
  "chest_pain", "shortness_of_breath", "dizziness", "rash", "itching",
  "joint_pain", "loss_of_appetite", "sneezing", "anxiety", "insomnia",
];

export default function PredictPage() {
  const [selected, setSelected] = useState<string[]>([]);
  const [custom, setCustom] = useState("");
  const [mode, setMode] = useState("patient");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<PredictResponse | null>(null);
  const [error, setError] = useState("");

  const toggle = (s: string) => {
    setSelected((prev) =>
      prev.includes(s) ? prev.filter((x) => x !== s) : [...prev, s]
    );
  };

  const addCustom = () => {
    const parts = custom
      .split(/[,،]/)
      .map((s) => s.trim().toLowerCase().replace(/\s+/g, "_"))
      .filter(Boolean);
    setSelected((prev) => Array.from(new Set([...prev, ...parts])));
    setCustom("");
  };

  const runPredict = async () => {
    if (selected.length === 0) {
      setError("Please select or enter at least one symptom.");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await predictDiseases(selected, mode);
      setResult(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || "Prediction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Disease Prediction</h2>
        <p className="text-slate-400 mt-1">
          Select symptoms. Results are probabilistic decision support only — not a diagnosis.
        </p>
      </div>

      <div className="card-3d space-y-5">
        <div>
          <label className="block text-sm font-medium text-slate-200 mb-2">Mode</label>
          <select
            className="input max-w-xs"
            value={mode}
            onChange={(e) => setMode(e.target.value)}
          >
            <option value="patient">Patient</option>
            <option value="student">Student / Study</option>
            <option value="clinician">Clinician</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-200 mb-2">
            Common symptoms
          </label>
          <div className="flex flex-wrap gap-2">
            {COMMON_SYMPTOMS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => toggle(s)}
                className={`px-3 py-1.5 rounded-full text-sm border transition-colors ${
                  selected.includes(s)
                    ? "bg-primary-600 text-white border-primary-600"
                    : "bg-slate-900/50 text-slate-200 border-white/15 hover:border-primary-400"
                }`}
              >
                {s.replace(/_/g, " ")}
              </button>
            ))}
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-slate-200 mb-2">
            Add custom symptoms (comma separated)
          </label>
          <div className="flex gap-2">
            <input
              className="input"
              value={custom}
              onChange={(e) => setCustom(e.target.value)}
              placeholder="e.g. bukhar, khansi, pet dard"
              onKeyDown={(e) => e.key === "Enter" && addCustom()}
            />
            <button type="button" className="btn-secondary whitespace-nowrap" onClick={addCustom}>
              Add
            </button>
          </div>
        </div>

        {selected.length > 0 && (
          <div className="text-sm text-slate-400">
            Selected:{" "}
            <span className="font-medium text-slate-100">
              {selected.map((s) => s.replace(/_/g, " ")).join(", ")}
            </span>
          </div>
        )}

        {error && (
          <div className="text-sm text-medical-red bg-red-50 border border-red-200 rounded-lg px-4 py-2">
            {error}
          </div>
        )}

        <button
          className="btn-primary"
          onClick={runPredict}
          disabled={loading || selected.length === 0}
        >
          {loading ? "Analyzing…" : "Predict possible conditions"}
        </button>
      </div>

      {result && (
        <div className="space-y-4">
          {result.safety.emergency && (
            <div className="bg-red-100 border border-red-300 text-red-900 rounded-xl p-4 font-medium">
              🚨 {result.disclaimer}
            </div>
          )}

          {!result.safety.emergency && (
            <>
              <div className="card-3d">
                <h3 className="font-semibold text-lg mb-3">Possible conditions</h3>
                {result.predictions.length === 0 ? (
                  <p className="text-slate-400">No strong matches found. Please consult a doctor.</p>
                ) : (
                  <ul className="space-y-3">
                    {result.predictions.map((p) => (
                      <li
                        key={p.disease}
                        className="border border-white/10 rounded-lg p-4 hover:bg-white/5"
                      >
                        <div className="flex items-start justify-between gap-3">
                          <div>
                            <p className="font-medium text-white">{p.disease}</p>
                            <p className="text-sm text-slate-400 mt-0.5">{p.explanation}</p>
                            {p.matching_symptoms.length > 0 && (
                              <p className="text-xs text-slate-400 mt-1">
                                Matched: {p.matching_symptoms.join(", ")}
                              </p>
                            )}
                          </div>
                          <div className="text-right shrink-0">
                            <div className="text-lg font-semibold text-primary-700">
                              {(p.confidence * 100).toFixed(0)}%
                            </div>
                            <div className="text-xs text-slate-400">confidence</div>
                          </div>
                        </div>
                        <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
                          <div
                            className="h-full bar-glow rounded-full"
                            style={{ width: `${Math.min(p.confidence * 100, 100)}%` }}
                          />
                        </div>
                      </li>
                    ))}
                  </ul>
                )}
              </div>

              {result.safety.warnings?.length > 0 && (
                <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm text-amber-900 space-y-1">
                  {result.safety.warnings.map((w, i) => (
                    <p key={i}>• {w}</p>
                  ))}
                </div>
              )}

              <p className="text-sm text-slate-400 italic">{result.disclaimer}</p>
            </>
          )}
        </div>
      )}
    </div>
  );
}
