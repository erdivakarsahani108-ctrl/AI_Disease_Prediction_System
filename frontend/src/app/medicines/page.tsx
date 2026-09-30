"use client";

import { useState } from "react";
import { searchMedicines } from "@/lib/api";

export default function MedicinesPage() {
  const [q,setQ]=useState(""); const [system,setSystem]=useState(""); const [rows,setRows]=useState<any[]>([]);
  async function search(){ if(q.trim()) setRows(await searchMedicines(q,system||undefined)); }
  return <main className="max-w-5xl mx-auto space-y-6">
    <div className="card-3d"><h1 className="text-2xl font-bold">Verified Medicine Knowledge</h1>
      <p className="text-sm text-slate-400 mt-2">Only verified records should be used for clinical decision-support workflows.</p></div>
    <div className="card-3d flex gap-3 flex-wrap">
      <input className="input flex-1" placeholder="Generic / brand / manufacturer" value={q} onChange={e=>setQ(e.target.value)}/>
      <select className="input" value={system} onChange={e=>setSystem(e.target.value)}>
        <option value="">All systems</option><option>allopathy</option><option>ayurveda</option><option>homeopathy</option><option>unani</option><option>siddha</option>
      </select>
      <button className="btn-primary" onClick={search}>Search</button>
    </div>
    <div className="grid gap-3">{rows.map((m:any)=><article key={m.id} className="card-3d">
      <h2 className="font-semibold">{m.canonical_name} {m.brand_name ? `— ${m.brand_name}` : ""}</h2>
      <p className="text-xs text-slate-400">{m.medical_system} · {m.manufacturer||"Manufacturer unavailable"} · {m.verified?"Verified":"Unverified"}</p>
      <p className="text-sm mt-2">{(m.indications||[]).join(", ")||"No verified indication listed."}</p>
      <p className="text-xs mt-2 text-slate-500">Source: {m.source} · Evidence: {m.evidence_level}</p>
    </article>)}</div>
  </main>
}
