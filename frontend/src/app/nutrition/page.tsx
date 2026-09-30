"use client";

import { useState } from "react";
import { calculateNutrition, NutritionResponse } from "@/lib/api";

export default function NutritionPage() {
  const [weight, setWeight] = useState(70);
  const [height, setHeight] = useState(170);
  const [age, setAge] = useState(30);
  const [sex, setSex] = useState("male");
  const [activity, setActivity] = useState("moderate");
  const [goal, setGoal] = useState("maintain");
  const [conditions, setConditions] = useState("");
  const [allergies, setAllergies] = useState("");
  const [result, setResult] = useState<NutritionResponse | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setError("");
    setLoading(true);
    try {
      const data = await calculateNutrition({
        weight_kg: weight,
        height_cm: height,
        age,
        sex,
        activity_level: activity,
        goal,
        conditions: conditions ? conditions.split(",").map((s) => s.trim()) : undefined,
        allergies: allergies ? allergies.split(",").map((s) => s.trim()) : undefined,
      });
      setResult(data);
    } catch (e: any) {
      setError(e?.response?.data?.detail || e.message || "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">Nutrition Calculator</h2>
        <p className="text-slate-400 mt-1">
          BMI, BMR, TDEE, macro targets & disease-aware tips (educational estimates).
        </p>
      </div>

      <div className="card-3d grid sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Weight (kg)</label>
          <input className="input" type="number" value={weight} onChange={(e) => setWeight(+e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Height (cm)</label>
          <input className="input" type="number" value={height} onChange={(e) => setHeight(+e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Age</label>
          <input className="input" type="number" value={age} onChange={(e) => setAge(+e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Sex</label>
          <select className="input" value={sex} onChange={(e) => setSex(e.target.value)}>
            <option value="male">Male</option>
            <option value="female">Female</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Activity</label>
          <select className="input" value={activity} onChange={(e) => setActivity(e.target.value)}>
            <option value="sedentary">Sedentary</option>
            <option value="light">Light</option>
            <option value="moderate">Moderate</option>
            <option value="active">Active</option>
            <option value="very_active">Very active</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Goal</label>
          <select className="input" value={goal} onChange={(e) => setGoal(e.target.value)}>
            <option value="maintain">Maintain weight</option>
            <option value="lose">Lose weight</option>
            <option value="gain">Gain weight</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Conditions (comma separated)</label>
          <input className="input" placeholder="diabetes, hypertension, pcos" value={conditions} onChange={(e) => setConditions(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Allergies (comma separated)</label>
          <input className="input" placeholder="peanuts, gluten" value={allergies} onChange={(e) => setAllergies(e.target.value)} />
        </div>
        <div className="sm:col-span-2">
          {error && <p className="text-sm text-red-600 mb-2">{error}</p>}
          <button className="btn-primary" onClick={run} disabled={loading}>
            {loading ? "Calculating…" : "Calculate"}
          </button>
        </div>
      </div>

      {result && (
        <div className="space-y-4">
          <div className="grid sm:grid-cols-4 gap-3">
            {[
              { label: "BMI", value: `${result.bmi} (${result.category})` },
              { label: "BMR", value: `${result.bmr} kcal` },
              { label: "TDEE", value: `${result.tdee} kcal` },
              { label: "Calorie target", value: `${result.calorie_target} kcal` },
            ].map((x) => (
              <div key={x.label} className="card-3d text-center">
                <p className="text-xs text-slate-400">{x.label}</p>
                <p className="text-lg font-semibold text-white mt-1">{x.value}</p>
              </div>
            ))}
          </div>
          <div className="card-3d">
            <h3 className="font-semibold mb-2">Macro targets</h3>
            <p className="text-sm text-slate-200">
              Protein: <strong>{result.protein_g} g</strong> · Carbs: <strong>{result.carbs_g} g</strong> · Fat:{" "}
              <strong>{result.fat_g} g</strong>
            </p>
          </div>
          {result.general_tips.length > 0 && (
            <div className="card-3d">
              <h3 className="font-semibold mb-2">Guidance</h3>
              <ul className="text-sm text-slate-200 space-y-1 list-disc list-inside">
                {result.general_tips.map((t, i) => (
                  <li key={i}>{t}</li>
                ))}
              </ul>
            </div>
          )}
          {result.allergy_notes.length > 0 && (
            <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 text-sm">
              {result.allergy_notes.map((n, i) => (
                <p key={i}>{n}</p>
              ))}
            </div>
          )}
          <p className="text-sm text-slate-400 italic">{result.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
