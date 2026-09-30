"""Pydantic v2 request / response schemas."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    preferred_language: str = "en"
    mode: str = "patient"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferred_language: Optional[str] = None
    mode: Optional[str] = None
    age: Optional[int] = Field(None, ge=0, le=120)
    sex: Optional[str] = None
    height_cm: Optional[float] = Field(None, gt=0, le=300)
    weight_kg: Optional[float] = Field(None, gt=0, le=500)
    allergies: Optional[List[str]] = None
    conditions: Optional[List[str]] = None
    contact: Optional[str] = Field(None, min_length=7, max_length=40)


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: str
    email: str
    full_name: Optional[str]
    preferred_language: str
    mode: str
    age: Optional[int] = None
    sex: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    allergies: List[str] = []
    conditions: List[str] = []
    email_verified: bool = False
    contact_verified: bool = False
    created_at: datetime


class PredictRequest(BaseModel):
    symptoms: List[str] = Field(..., min_length=1, max_length=30)
    age: Optional[int] = Field(None, ge=0, le=120)
    sex: Optional[str] = None
    medical_system: Optional[str] = "allopathy"
    mode: str = "patient"

    @field_validator("symptoms")
    @classmethod
    def clean_symptoms(cls, v: List[str]) -> List[str]:
        return [s.strip().lower() for s in v if s.strip()]


class PredictionItem(BaseModel):
    disease: str
    confidence: float
    matching_symptoms: List[str]
    total_typical_symptoms: int
    explanation: str
    note: str = ""


class PredictResponse(BaseModel):
    predictions: List[PredictionItem]
    input_symptoms: List[str]
    model_version: str = "hybrid-rf-v2"
    disclaimer: str
    safety: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    mode: str = "patient"
    medical_system: Optional[str] = None
    conversation_id: Optional[str] = None
    language_hint: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    language: str
    language_name: str
    intent: str
    detected_symptoms: List[str] = []
    predictions: List[Dict[str, Any]] = []
    citations: List[Dict[str, Any]] = []
    safety: Dict[str, Any]
    mode: str
    medical_system: Optional[str] = None
    conversation_id: Optional[str] = None


class NutritionRequest(BaseModel):
    weight_kg: float = Field(..., gt=0, le=500)
    height_cm: float = Field(..., gt=0, le=300)
    age: int = Field(..., ge=1, le=120)
    sex: str = "male"
    activity_level: str = "moderate"
    goal: str = "maintain"
    conditions: Optional[List[str]] = None
    contact: Optional[str] = Field(None, min_length=7, max_length=40)
    allergies: Optional[List[str]] = None


class NutritionResponse(BaseModel):
    bmi: float
    category: str
    bmr: float
    tdee: float
    activity_level: str
    calorie_target: float
    protein_g: float
    carbs_g: float
    fat_g: float
    general_tips: List[str] = []
    allergy_notes: List[str] = []
    goal: str
    disclaimer: str


class KnowledgeSearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    query: str
    count: int


class MedicalSystemOut(BaseModel):
    id: str
    name: str
    description: str


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


class VoiceScanRequest(BaseModel):
    transcript: str = Field(..., min_length=1, max_length=5000)
    mode: str = "patient"
    consent_given: bool = False
    audio_quality: Optional[Dict[str, Any]] = None


class VoiceScanResponse(BaseModel):
    ok: bool
    emergency: bool = False
    transcript: Optional[str] = None
    language: Optional[str] = None
    language_name: Optional[str] = None
    detected_symptoms: List[str] = []
    predictions: List[Dict[str, Any]] = []
    citations: List[Dict[str, Any]] = []
    reply: Optional[str] = None
    safety: Optional[Dict[str, Any]] = None
    quality_notes: List[str] = []
    modality: Optional[str] = None
    disclaimer: Optional[str] = None
    error: Optional[str] = None
    code: Optional[str] = None


class MultimodalScanRequest(BaseModel):
    """Image/document scan metadata + optional user description (no raw medical image diagnosis)."""
    description: str = Field(..., min_length=1, max_length=2000)
    modality: str = "general_image"  # skin_image | document | eye_image | general_image
    consent_given: bool = False
    quality: Optional[Dict[str, Any]] = None  # blur, lighting scores from client
    mode: str = "patient"


class OtpRequest(BaseModel):
    purpose: str = Field(..., pattern="^(email_verification|contact_verification|ownership_transfer)$")
    channel: str = Field(..., pattern="^(email|contact)$")
    destination: str = Field(..., min_length=3, max_length=255)


class OtpVerify(BaseModel):
    challenge_id: str
    code: str = Field(..., min_length=6, max_length=8)


class TransferCreate(BaseModel):
    organization_id: str
    recipient_email: EmailStr


class TransferAccept(BaseModel):
    transfer_id: str
    email_challenge_id: str
    contact_challenge_id: str


class MedicineSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)
    medical_system: Optional[str] = None
    verified_only: bool = True
    limit: int = Field(20, ge=1, le=100)


class MedicineOut(BaseModel):
    id: str
    canonical_name: str
    brand_name: Optional[str]
    manufacturer: Optional[str]
    medical_system: str
    active_ingredients: List[Any] = []
    dosage_form: Optional[str]
    strength: Optional[str]
    route: Optional[str]
    indications: List[Any] = []
    contraindications: List[Any] = []
    interactions: List[Any] = []
    allergy_warnings: List[Any] = []
    source: str
    jurisdiction: Optional[str]
    evidence_level: str
    verified: bool


class ScanRequest(BaseModel):
    modality: str = Field(..., pattern="^(document|skin_image|eye_image|general_image|lab_report|prescription|pathology)$")
    description: str = Field(..., min_length=1, max_length=10000)
    consent_given: bool = False
    quality: Dict[str, Any] = {}


class TransferStatus(BaseModel):
    transfer_id: str
    status: str
    email_verified: bool
    contact_verified: bool
