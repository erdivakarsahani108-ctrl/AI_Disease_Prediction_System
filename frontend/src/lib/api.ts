import axios from "axios";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export const api = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// Attach JWT if present
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("access_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export interface PredictionItem {
  disease: string;
  confidence: number;
  matching_symptoms: string[];
  total_typical_symptoms: number;
  explanation: string;
  note?: string;
}

export interface PredictResponse {
  predictions: PredictionItem[];
  input_symptoms: string[];
  model_version: string;
  disclaimer: string;
  safety: {
    risk_level: string;
    emergency: boolean;
    warnings: string[];
    requires_escalation?: boolean;
  };
}

export interface ChatResponse {
  reply: string;
  language: string;
  language_name: string;
  intent: string;
  detected_symptoms: string[];
  predictions: any[];
  citations: any[];
  safety: any;
  mode: string;
  medical_system?: string;
  conversation_id?: string;
}

export interface NutritionResponse {
  bmi: number;
  category: string;
  bmr: number;
  tdee: number;
  activity_level: string;
  calorie_target: number;
  protein_g: number;
  carbs_g: number;
  fat_g: number;
  general_tips: string[];
  allergy_notes: string[];
  goal: string;
  disclaimer: string;
}

export interface UserOut {
  id: string;
  email: string;
  full_name?: string;
  preferred_language: string;
  mode: string;
  age?: number;
  sex?: string;
  height_cm?: number;
  weight_kg?: number;
  allergies: string[];
  conditions: string[];
  created_at: string;
}

export async function register(email: string, password: string, full_name?: string) {
  const { data } = await api.post("/auth/register", { email, password, full_name });
  return data;
}

export async function login(email: string, password: string) {
  const { data } = await api.post("/auth/login", { email, password });
  if (typeof window !== "undefined") {
    localStorage.setItem("access_token", data.access_token);
    localStorage.setItem("refresh_token", data.refresh_token);
  }
  return data;
}

export function logout() {
  if (typeof window !== "undefined") {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
  }
}

export async function getMe(): Promise<UserOut> {
  const { data } = await api.get("/auth/me");
  return data;
}

export async function predictDiseases(symptoms: string[], mode = "patient") {
  const { data } = await api.post<PredictResponse>("/predict", { symptoms, mode });
  return data;
}

export async function getPredictionHistory() {
  const { data } = await api.get("/predict/history");
  return data;
}

export async function sendChat(message: string, mode = "patient", medical_system?: string) {
  const { data } = await api.post<ChatResponse>("/chat", { message, mode, medical_system });
  return data;
}

export async function calculateNutrition(payload: {
  weight_kg: number;
  height_cm: number;
  age: number;
  sex: string;
  activity_level: string;
  goal: string;
  conditions?: string[];
  allergies?: string[];
}) {
  const { data } = await api.post<NutritionResponse>("/nutrition/calculate", payload);
  return data;
}

export async function getDashboard() {
  const { data } = await api.get("/dashboard");
  return data;
}

export async function getSystems() {
  const { data } = await api.get("/systems");
  return data;
}


export async function requestOtp(purpose: "email_verification"|"contact_verification"|"ownership_transfer",
  channel: "email"|"contact", destination: string) {
  const { data } = await api.post("/auth/otp/request", { purpose, channel, destination });
  return data;
}

export async function verifyOtp(challenge_id: string, code: string) {
  const { data } = await api.post("/auth/otp/verify", { challenge_id, code });
  return data;
}

export async function createOrganization(name: string, slug: string) {
  const { data } = await api.post("/organizations", null, { params: { name, slug } });
  return data;
}

export async function createOwnershipTransfer(organization_id: string, recipient_email: string) {
  const { data } = await api.post("/organizations/transfer", { organization_id, recipient_email });
  return data;
}

export async function searchMedicines(query: string, medical_system?: string) {
  const { data } = await api.post("/medicines/search", {
    query, medical_system, verified_only: true, limit: 30
  });
  return data;
}

export async function analyzeScan(modality: string, description: string, quality: any = {}) {
  const { data } = await api.post("/scan/analyze", {
    modality, description, quality, consent_given: true
  });
  return data;
}
