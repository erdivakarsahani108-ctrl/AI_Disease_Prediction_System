"use client";

import { useState } from "react";
import { createOrganization, createOwnershipTransfer, requestOtp, verifyOtp } from "@/lib/api";

export default function AdminPage() {
  const [orgName,setOrgName]=useState(""); const [slug,setSlug]=useState("");
  const [orgId,setOrgId]=useState(""); const [recipient,setRecipient]=useState("");
  const [emailChallenge,setEmailChallenge]=useState(""); const [contactChallenge,setContactChallenge]=useState("");
  const [emailCode,setEmailCode]=useState(""); const [contactCode,setContactCode]=useState("");
  const [msg,setMsg]=useState("");

  async function bootstrap() {
    try { const x=await createOrganization(orgName,slug); setOrgId(x.id); setMsg(`Organization created: ${x.id}`); }
    catch(e:any){setMsg(e?.response?.data?.detail||"Unable to create organization");}
  }
  async function transfer() {
    try { const x=await createOwnershipTransfer(orgId,recipient); setMsg(`Transfer created: ${x.transfer_id}`); }
    catch(e:any){setMsg(e?.response?.data?.detail||"Transfer failed");}
  }
  async function verifyEmail() {
    try { const x=await requestOtp("email_verification","email",recipient); setEmailChallenge(x.challenge_id); setMsg("Email verification challenge created."); }
    catch(e:any){setMsg(e?.response?.data?.detail||"OTP request failed");}
  }
  async function verifyContact() {
    try { const x=await requestOtp("contact_verification","contact","verified-contact"); setContactChallenge(x.challenge_id); setMsg("Contact verification challenge created."); }
    catch(e:any){setMsg(e?.response?.data?.detail||"OTP request failed");}
  }
  async function accept() {
    setMsg("Recipient acceptance must be completed by the recipient's authenticated account using both verified channels.");
  }

  return <main className="max-w-3xl mx-auto space-y-6">
    <div className="card-3d"><h1 className="text-2xl font-bold">Organization & White-label Security</h1>
      <p className="text-sm text-slate-400 mt-2">Ownership transfer is consent-based and audited. It cannot be used to impersonate another person.</p>
    </div>
    <div className="card-3d space-y-3">
      <h2 className="font-semibold">Create organization</h2>
      <input className="input" placeholder="Organization name" value={orgName} onChange={e=>setOrgName(e.target.value)}/>
      <input className="input" placeholder="Unique slug" value={slug} onChange={e=>setSlug(e.target.value)}/>
      <button className="btn-primary" onClick={bootstrap}>Create</button>
    </div>
    <div className="card-3d space-y-3">
      <h2 className="font-semibold">Transfer ownership</h2>
      <input className="input" placeholder="Organization ID" value={orgId} onChange={e=>setOrgId(e.target.value)}/>
      <input className="input" placeholder="Recipient verified email" value={recipient} onChange={e=>setRecipient(e.target.value)}/>
      <button className="btn-primary" onClick={transfer}>Create transfer</button>
      <div className="grid sm:grid-cols-2 gap-3">
        <button className="btn-secondary" onClick={verifyEmail}>Request email verification</button>
        <button className="btn-secondary" onClick={verifyContact}>Request contact verification</button>
      </div>
      <input className="input" placeholder="Email OTP" value={emailCode} onChange={e=>setEmailCode(e.target.value)}/>
      <input className="input" placeholder="Contact OTP" value={contactCode} onChange={e=>setContactCode(e.target.value)}/>
      <p className="text-xs text-slate-500">Challenges: {emailChallenge || "—"} / {contactChallenge || "—"}</p>
      <button className="btn-secondary" onClick={accept}>Prepare recipient acceptance</button>
    </div>
    {msg && <div className="card-3d text-sm">{msg}</div>}
  </main>
}
