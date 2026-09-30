"use client";

import { useState } from "react";
import { analyzeScan } from "@/lib/api";

export default function ScanPage() {
  const [modality,setModality]=useState("document");
  const [description,setDescription]=useState("");
  const [result,setResult]=useState<any>(null);
  const [error,setError]=useState("");

  async function run() {
    setError(""); setResult(null);
    if(!description.trim()){setError("Describe or upload the input first.");return;}
    try { setResult(await analyzeScan(modality,description,{completeness:1})); }
    catch(e:any){setError(e?.response?.data?.detail||"Scan failed");}
  }

  return <main className="max-w-3xl mx-auto space-y-6">
    <div className="card-3d">
      <h1 className="text-2xl font-bold">Advanced Medical Scan</h1>
      <p className="text-sm text-slate-400 mt-2">Structured extraction and safety triage. It does not establish a diagnosis.</p>
    </div>
    <div className="card-3d space-y-4">
      <select className="input" value={modality} onChange={e=>setModality(e.target.value)}>
        {["document","lab_report","prescription","pathology","skin_image","eye_image","general_image"].map(x=><option key={x}>{x}</option>)}
      </select>
      <textarea className="input min-h-40" placeholder="Paste report text or describe the scan/input..." value={description} onChange={e=>setDescription(e.target.value)}/>
      <label className="flex gap-2 text-sm"><input type="checkbox" defaultChecked/> I consent to processing this medical information.</label>
      <button className="btn-primary" onClick={run}>Analyze safely</button>
    </div>
    {error && <div className="card-3d text-red-300">{error}</div>}
    {result && <pre className="card-3d overflow-auto text-xs">{JSON.stringify(result,null,2)}</pre>}
  </main>
}
