"""SQLAlchemy ORM models — persistent storage."""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, JSON, Index
)
from sqlalchemy.orm import relationship

from app.db.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    preferred_language = Column(String(20), default="en")
    role = Column(String(30), default="patient")  # patient | student | clinician | admin
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    contact = Column(String(40), nullable=True)
    contact_verified = Column(Boolean, default=False, nullable=False)
    age = Column(Integer, nullable=True)
    sex = Column(String(20), nullable=True)
    height_cm = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=True)
    allergies = Column(JSON, default=list)  # list of strings
    conditions = Column(JSON, default=list)  # known conditions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    predictions = relationship("PredictionRecord", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    nutrition_logs = relationship("NutritionLog", back_populates="user", cascade="all, delete-orphan")


class PredictionRecord(Base):
    __tablename__ = "prediction_records"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    symptoms = Column(JSON, nullable=False)
    results = Column(JSON, nullable=False)  # list of prediction dicts
    top_disease = Column(String(255), nullable=True)
    top_confidence = Column(Float, nullable=True)
    mode = Column(String(30), default="patient")
    safety_risk = Column(String(30), nullable=True)
    model_version = Column(String(50), default="hybrid-rf-v2")
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="predictions")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    title = Column(String(255), default="Chat")
    mode = Column(String(30), default="patient")
    medical_system = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=_uuid)
    conversation_id = Column(String(36), ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # user | assistant
    content = Column(Text, nullable=False)
    language = Column(String(20), nullable=True)
    intent = Column(String(50), nullable=True)
    citations = Column(JSON, default=list)
    safety = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="messages")


class KnowledgeDocument(Base):
    """Structured medical knowledge for RAG-style retrieval."""
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=_uuid)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    content_hi = Column(Text, nullable=True)
    medical_system = Column(String(50), default="allopathy", index=True)
    category = Column(String(100), nullable=True)  # disease, nutrition, lifestyle, emergency
    tags = Column(JSON, default=list)
    source = Column(String(255), default="educational-synthetic")
    evidence_level = Column(String(50), default="educational")  # educational | guideline | research
    language = Column(String(20), default="en")
    is_verified = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_knowledge_tags", "category"),
    )


class NutritionLog(Base):
    __tablename__ = "nutrition_logs"

    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    bmi = Column(Float, nullable=True)
    bmr = Column(Float, nullable=True)
    tdee = Column(Float, nullable=True)
    calorie_target = Column(Float, nullable=True)
    protein_g = Column(Float, nullable=True)
    carbs_g = Column(Float, nullable=True)
    fat_g = Column(Float, nullable=True)
    activity_level = Column(String(30), nullable=True)
    goal = Column(String(30), nullable=True)  # maintain | lose | gain
    diet_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="nutrition_logs")


class Organization(Base):
    __tablename__ = "organizations"
    id = Column(String(36), primary_key=True, default=_uuid)
    name = Column(String(255), nullable=False)
    slug = Column(String(120), unique=True, nullable=False, index=True)
    owner_user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(String(30), default="active", nullable=False)
    branding = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OrganizationMember(Base):
    __tablename__ = "organization_members"
    id = Column(String(36), primary_key=True, default=_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    role = Column(String(30), default="member", nullable=False)
    status = Column(String(30), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class OtpChallenge(Base):
    __tablename__ = "otp_challenges"
    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    purpose = Column(String(50), nullable=False, index=True)
    channel = Column(String(20), nullable=False)
    destination_hash = Column(String(128), nullable=False)
    code_hash = Column(String(128), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    consumed = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class OwnershipTransfer(Base):
    __tablename__ = "ownership_transfers"
    id = Column(String(36), primary_key=True, default=_uuid)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    from_user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    to_email = Column(String(255), nullable=False, index=True)
    status = Column(String(30), default="pending", nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    contact_verified = Column(Boolean, default=False, nullable=False)
    accepted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(String(36), primary_key=True, default=_uuid)
    actor_user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    organization_id = Column(String(36), nullable=True, index=True)
    action = Column(String(120), nullable=False, index=True)
    target_type = Column(String(80), nullable=True)
    target_id = Column(String(120), nullable=True)
    request_id = Column(String(120), nullable=True, index=True)
    metadata_json = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class Medicine(Base):
    __tablename__ = "medicines"
    id = Column(String(36), primary_key=True, default=_uuid)
    canonical_name = Column(String(500), nullable=False, index=True)
    brand_name = Column(String(500), nullable=True, index=True)
    manufacturer = Column(String(500), nullable=True)
    medical_system = Column(String(80), nullable=False, index=True)
    active_ingredients = Column(JSON, default=list)
    dosage_form = Column(String(120), nullable=True)
    strength = Column(String(120), nullable=True)
    route = Column(String(120), nullable=True)
    indications = Column(JSON, default=list)
    contraindications = Column(JSON, default=list)
    adverse_effects = Column(JSON, default=list)
    interactions = Column(JSON, default=list)
    allergy_warnings = Column(JSON, default=list)
    source = Column(String(500), nullable=False)
    source_version = Column(String(120), nullable=True)
    jurisdiction = Column(String(120), nullable=True)
    regulator_id = Column(String(255), nullable=True)
    evidence_level = Column(String(50), default="unverified")
    verified = Column(Boolean, default=False, nullable=False)
    review_due_at = Column(DateTime, nullable=True)
    provenance_hash = Column(String(128), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class MedicalDocument(Base):
    __tablename__ = "medical_documents"
    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    document_type = Column(String(80), nullable=False)
    filename = Column(String(500), nullable=True)
    source = Column(String(500), nullable=True)
    extracted_text = Column(Text, nullable=True)
    findings = Column(JSON, default=list)
    quality = Column(JSON, default=dict)
    consent = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ScanEvent(Base):
    __tablename__ = "scan_events"
    id = Column(String(36), primary_key=True, default=_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    modality = Column(String(80), nullable=False)
    input_hash = Column(String(128), nullable=True, index=True)
    quality = Column(JSON, default=dict)
    result = Column(JSON, default=dict)
    safety = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)
