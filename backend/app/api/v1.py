"""API v1 routes — DB-backed auth, predictions, chat, nutrition, knowledge."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.rate_limit import rate_limit_dependency
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.core.safety import run_safety_pipeline, UserMode
from app.db.database import get_db
from app.db.models import (
    AuditEvent, Organization, OrganizationMember, OwnershipTransfer, Medicine,
    ChatMessage,
    Conversation,
    NutritionLog,
    PredictionRecord,
    User,
)
from app.ml.predictor import get_predictor
from app.models.schemas import (
    VoiceScanRequest,
    VoiceScanResponse,
    MultimodalScanRequest,
    ChatRequest,
    ChatResponse,
    HealthResponse,
    KnowledgeSearchResponse,
    MedicalSystemOut,
    NutritionRequest,
    NutritionResponse,
    PredictRequest,
    PredictResponse,
    PredictionItem,
    Token,
    UserCreate,
    UserLogin,
    UserOut,
    UserUpdate,
    OtpRequest, OtpVerify, TransferCreate, TransferAccept, TransferStatus, MedicineSearchRequest, MedicineOut, ScanRequest,
)
from app.services.chatbot import ChatbotService
from app.services.nutrition import full_nutrition_profile
from app.services.rag import retrieve
from app.services.secure_transfer import issue_otp, verify_otp, audit
from app.services.medicine_catalog import search_medicines
from app.services.scan_engine import analyze_description

settings = get_settings()
router = APIRouter()
security = HTTPBearer(auto_error=False)
_CHATBOT = ChatbotService()


def get_current_user(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> Optional[User]:
    if not creds:
        return None
    payload = decode_token(creds.credentials)
    if not payload or payload.get("type") != "access":
        return None
    email = payload.get("sub")
    return db.query(User).filter(User.email == email, User.is_active == True).first()


def require_user(user: Optional[User] = Depends(get_current_user)) -> User:
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


# ---------- Health ----------
@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow(),
    )


# ---------- Auth ----------
@router.post("/auth/register", response_model=UserOut)
async def register(body: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=body.email,
        hashed_password=get_password_hash(body.password),
        full_name=body.full_name,
        preferred_language=body.preferred_language,
        role=body.mode if body.mode in ("patient", "student") else "patient",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        preferred_language=user.preferred_language,
        mode=user.role,
        age=user.age,
        sex=user.sex,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        allergies=user.allergies or [],
        conditions=user.conditions or [],
        email_verified=user.email_verified,
        contact_verified=user.contact_verified,
        created_at=user.created_at,
    )


@router.post("/auth/login", response_model=Token)
async def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return Token(
        access_token=create_access_token(user.email, {"role": user.role, "uid": user.id}),
        refresh_token=create_refresh_token(user.email),
    )


@router.get("/auth/me", response_model=UserOut)
async def me(user: User = Depends(require_user)):
    return UserOut(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        preferred_language=user.preferred_language,
        mode=user.role,
        age=user.age,
        sex=user.sex,
        height_cm=user.height_cm,
        weight_kg=user.weight_kg,
        allergies=user.allergies or [],
        conditions=user.conditions or [],
        email_verified=user.email_verified,
        contact_verified=user.contact_verified,
        created_at=user.created_at,
    )


@router.patch("/auth/me", response_model=UserOut)
async def update_me(body: UserUpdate, user: User = Depends(require_user), db: Session = Depends(get_db)):
    for field in ("full_name", "preferred_language", "age", "sex", "height_cm", "weight_kg", "contact"):
        val = getattr(body, field, None)
        if val is not None:
            setattr(user, field, val)
    if body.allergies is not None:
        user.allergies = body.allergies
    if body.conditions is not None:
        user.conditions = body.conditions
    # Privileged roles cannot be self-assigned from profile update; use an audited admin workflow.
    db.commit()
    db.refresh(user)
    return await me(user)



# ---------- Verification / Organization ----------
@router.post("/auth/otp/request")
async def request_otp(body: OtpRequest, user: User = Depends(require_user), db: Session = Depends(get_db)):
    destination = body.destination.strip()
    if body.channel == "email" and destination.lower() != user.email.lower():
        raise HTTPException(status_code=403, detail="Email destination must match the authenticated account.")
    if body.channel == "contact" and destination != (user.contact or ""):
        raise HTTPException(status_code=403, detail="Contact destination must match the verified account contact.")
    ch, dev_code = issue_otp(db, user.id, body.purpose, body.channel, destination)
    # Development convenience only. Production delivery must use an email/SMS provider and DEV_OTP_RETURN=false.
    if settings.DEBUG:
        return {"challenge_id": ch.id, "expires_at": ch.expires_at, "dev_code": dev_code}
    return {"challenge_id": ch.id, "expires_at": ch.expires_at}

@router.post("/auth/otp/verify")
async def verify_auth_otp(body: OtpVerify, user: User = Depends(require_user), db: Session = Depends(get_db)):
    ok, msg = verify_otp(db, body.challenge_id, body.code, user.id)
    if not ok:
        raise HTTPException(status_code=400, detail=msg)
    ch=db.query(__import__("app.db.models", fromlist=["OtpChallenge"]).OtpChallenge).filter_by(id=body.challenge_id).first()
    if ch.purpose=="email_verification": user.email_verified=True
    if ch.purpose=="contact_verification": user.contact_verified=True
    db.commit()
    audit(db,user.id,"otp_verified","otp_challenge",body.challenge_id,metadata={"purpose":ch.purpose})
    return {"verified":True,"purpose":ch.purpose}

@router.post("/organizations")
async def create_organization(name: str, slug: str, user: User = Depends(require_user), db: Session = Depends(get_db)):
    if db.query(Organization).filter(Organization.slug==slug).first():
        raise HTTPException(status_code=409, detail="Slug already exists")
    org=Organization(name=name.strip(), slug=slug.strip().lower(), owner_user_id=user.id)
    db.add(org); db.flush()
    db.add(OrganizationMember(organization_id=org.id,user_id=user.id,role="owner"))
    audit(db,user.id,"organization_created","organization",org.id,org.id,{"slug":org.slug})
    return {"id":org.id,"name":org.name,"slug":org.slug,"owner_user_id":user.id}

@router.post("/organizations/transfer", response_model=TransferStatus)
async def create_transfer(body: TransferCreate, user: User = Depends(require_user), db: Session = Depends(get_db)):
    org=db.query(Organization).filter(Organization.id==body.organization_id,Organization.owner_user_id==user.id).first()
    if not org: raise HTTPException(status_code=403, detail="Only the verified organization owner can transfer ownership.")
    if not user.email_verified or not user.contact_verified:
        raise HTTPException(status_code=403, detail="Verify both email and contact before ownership transfer.")
    from datetime import timedelta
    t=OwnershipTransfer(organization_id=org.id,from_user_id=user.id,to_email=body.recipient_email.lower(),
                        expires_at=datetime.utcnow()+timedelta(hours=24))
    db.add(t); db.commit(); db.refresh(t)
    audit(db,user.id,"ownership_transfer_created","organization",org.id,org.id,{"recipient":body.recipient_email.lower()})
    return TransferStatus(transfer_id=t.id,status=t.status,email_verified=False,contact_verified=False)

@router.post("/organizations/transfer/accept-code")
async def accept_transfer(transfer_id: str, email_challenge_id: str, email_code: str,
                           contact_challenge_id: str, contact_code: str,
                           user: User = Depends(require_user), db: Session = Depends(get_db)):
    t=db.query(OwnershipTransfer).filter(OwnershipTransfer.id==transfer_id,
                                          OwnershipTransfer.to_email==user.email.lower(),
                                          OwnershipTransfer.status=="pending").first()
    if not t: raise HTTPException(status_code=404, detail="Transfer not found.")
    if t.expires_at < datetime.utcnow(): t.status="expired"; db.commit(); raise HTTPException(status_code=400,detail="Transfer expired.")
    if not user.email_verified or not user.contact_verified:
        raise HTTPException(status_code=403, detail="Recipient email and contact must be verified.")
    eok,emsg=verify_otp(db,email_challenge_id,email_code,user.id)
    cok,cmsg=verify_otp(db,contact_challenge_id,contact_code,user.id)
    if not eok or not cok: raise HTTPException(status_code=400,detail=f"OTP verification failed: {emsg if not eok else cmsg}")
    org=db.query(Organization).filter(Organization.id==t.organization_id).first()
    old_owner=org.owner_user_id
    org.owner_user_id=user.id
    t.status="accepted"; t.email_verified=True; t.contact_verified=True; t.accepted_at=datetime.utcnow()
    db.add(OrganizationMember(organization_id=org.id,user_id=user.id,role="owner"))
    audit(db,old_owner,"ownership_transferred","organization",org.id,org.id,{"new_owner":user.id,"transfer_id":t.id})
    audit(db,user.id,"ownership_transfer_accepted","organization",org.id,org.id,{"old_owner":old_owner,"transfer_id":t.id})
    db.commit()
    return {"ok":True,"organization_id":org.id,"new_owner_user_id":user.id,"transfer_id":t.id}

# ---------- Medicine catalog ----------
@router.post("/medicines/search", response_model=List[MedicineOut])
async def medicines(body: MedicineSearchRequest, db: Session = Depends(get_db)):
    rows=search_medicines(db,body.query,body.medical_system,body.verified_only,body.limit)
    return [MedicineOut.model_validate({
        "id":m.id,"canonical_name":m.canonical_name,"brand_name":m.brand_name,
        "manufacturer":m.manufacturer,"medical_system":m.medical_system,
        "active_ingredients":m.active_ingredients or [],"dosage_form":m.dosage_form,
        "strength":m.strength,"route":m.route,"indications":m.indications or [],
        "contraindications":m.contraindications or [],"interactions":m.interactions or [],
        "allergy_warnings":m.allergy_warnings or [],"source":m.source,
        "jurisdiction":m.jurisdiction,"evidence_level":m.evidence_level,"verified":m.verified
    }) for m in rows]

# ---------- Safe scan ----------
@router.post("/scan/analyze")
async def scan(body: ScanRequest, user: Optional[User]=Depends(get_current_user), db: Session=Depends(get_db)):
    if not body.consent_given:
        raise HTTPException(status_code=400,detail="Explicit consent is required before medical scan processing.")
    result=analyze_description(body.modality,body.description,body.quality)
    from app.db.models import ScanEvent
    event=ScanEvent(user_id=user.id if user else None,modality=body.modality,
                    input_hash=result["input_hash"],quality=body.quality,result=result,
                    safety={"requires_human_review":result["requires_human_review"]})
    db.add(event); db.commit()
    return result

# ---------- Predict ----------
@router.post("/predict", response_model=PredictResponse, dependencies=[Depends(rate_limit_dependency)])
async def predict(
    body: PredictRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    mode = body.mode or (user.role if user else "patient")
    safety = run_safety_pipeline(
        " ".join(body.symptoms),
        mode=UserMode(mode) if mode in UserMode._value2member_map_ else UserMode.PATIENT,
    )
    if safety.emergency_detected:
        return PredictResponse(
            predictions=[],
            input_symptoms=body.symptoms,
            model_version=get_predictor().MODEL_VERSION,
            disclaimer=safety.disclaimer,
            safety={"risk_level": safety.risk_level.value, "emergency": True, "warnings": safety.warnings},
        )

    predictor = get_predictor()
    raw = predictor.predict(body.symptoms, top_k=5)
    conf = raw[0]["confidence"] if raw else 0.0
    safety = run_safety_pipeline(
        " ".join(body.symptoms),
        mode=UserMode(mode) if mode in UserMode._value2member_map_ else UserMode.PATIENT,
        prediction_confidence=conf,
    )
    items = [PredictionItem(**{k: v for k, v in p.items() if k in PredictionItem.model_fields}) for p in raw]

    # Persist if logged in
    if user:
        rec = PredictionRecord(
            user_id=user.id,
            symptoms=body.symptoms,
            results=raw,
            top_disease=raw[0]["disease"] if raw else None,
            top_confidence=conf if raw else None,
            mode=mode,
            safety_risk=safety.risk_level.value,
            model_version=predictor.MODEL_VERSION,
        )
        db.add(rec)
        db.commit()

    return PredictResponse(
        predictions=items,
        input_symptoms=body.symptoms,
        model_version=predictor.MODEL_VERSION,
        disclaimer=safety.disclaimer,
        safety={
            "risk_level": safety.risk_level.value,
            "emergency": safety.emergency_detected,
            "warnings": safety.warnings,
            "requires_escalation": safety.requires_escalation,
        },
    )


@router.get("/predict/history")
async def prediction_history(
    limit: int = 20,
    user: User = Depends(require_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.user_id == user.id)
        .order_by(PredictionRecord.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": r.id,
            "symptoms": r.symptoms,
            "top_disease": r.top_disease,
            "top_confidence": r.top_confidence,
            "results": r.results,
            "mode": r.mode,
            "created_at": r.created_at.isoformat(),
        }
        for r in rows
    ]


# ---------- Chat ----------
@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(rate_limit_dependency)])
async def chat(
    body: ChatRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    mode = body.mode or (user.role if user else "patient")
    result = _CHATBOT.chat(
        message=body.message,
        db=db,
        mode=mode,
        medical_system=body.medical_system,
        conversation_id=body.conversation_id,
    )

    # Persist conversation if logged in
    if user:
        conv_id = body.conversation_id
        conv = None
        if conv_id:
            conv = db.query(Conversation).filter(
                Conversation.id == conv_id, Conversation.user_id == user.id
            ).first()
        if not conv:
            conv = Conversation(
                user_id=user.id,
                title=body.message[:60],
                mode=mode,
                medical_system=body.medical_system,
            )
            db.add(conv)
            db.flush()
        db.add(ChatMessage(
            conversation_id=conv.id,
            role="user",
            content=body.message,
            language=result.get("language"),
        ))
        db.add(ChatMessage(
            conversation_id=conv.id,
            role="assistant",
            content=result["reply"],
            language=result.get("language"),
            intent=result.get("intent"),
            citations=result.get("citations"),
            safety=result.get("safety"),
        ))
        db.commit()
        result["conversation_id"] = conv.id

    return ChatResponse(**{k: v for k, v in result.items() if k in ChatResponse.model_fields or k == "conversation_id"})


# ---------- Nutrition ----------
@router.post("/nutrition/calculate", response_model=NutritionResponse)
async def nutrition_calc(
    body: NutritionRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    profile = full_nutrition_profile(
        weight_kg=body.weight_kg,
        height_cm=body.height_cm,
        age=body.age,
        sex=body.sex,
        activity=body.activity_level,
        goal=body.goal,
        conditions=body.conditions or (user.conditions if user else None),
        allergies=body.allergies or (user.allergies if user else None),
    )
    if user:
        log = NutritionLog(
            user_id=user.id,
            bmi=profile["bmi"],
            bmr=profile["bmr"],
            tdee=profile["tdee"],
            calorie_target=profile["calorie_target"],
            protein_g=profile["protein_g"],
            carbs_g=profile["carbs_g"],
            fat_g=profile["fat_g"],
            activity_level=body.activity_level,
            goal=body.goal,
            diet_notes="; ".join(profile.get("general_tips", [])[:3]),
        )
        db.add(log)
        # update profile anthropometrics
        user.weight_kg = body.weight_kg
        user.height_cm = body.height_cm
        user.age = body.age
        user.sex = body.sex
        db.commit()
    return NutritionResponse(**profile)


# ---------- Knowledge ----------
@router.get("/knowledge/search", response_model=KnowledgeSearchResponse)
async def knowledge_search(
    q: str,
    system: Optional[str] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    results = retrieve(db, q, medical_system=system, top_k=limit)
    return KnowledgeSearchResponse(results=results, query=q, count=len(results))


# ---------- Systems ----------
@router.get("/systems", response_model=List[MedicalSystemOut])
async def list_systems():
    descriptions = {
        "allopathy": "Modern / Western medicine based on scientific evidence",
        "ayurveda": "Traditional Indian system emphasizing balance of doshas",
        "homeopathy": "System based on like-cures-like and individualization",
        "unani": "Greco-Arabic traditional medicine",
        "siddha": "Ancient South Indian system",
        "yoga_naturopathy": "Yoga and natural healing approaches",
        "naturopathy": "Nature-based therapeutic approaches",
        "acupuncture": "Traditional Chinese needle therapy",
        "acupressure": "Pressure-point based therapy",
        "physiotherapy": "Physical therapy and rehabilitation",
        "chiropractic": "Spine and musculoskeletal focused care",
        "aromatherapy": "Essential-oil based complementary therapy",
        "reiki": "Energy-based complementary practice",
    }
    return [
        MedicalSystemOut(id=s, name=s.replace("_", " ").title(), description=descriptions.get(s, ""))
        for s in settings.MEDICAL_SYSTEMS
    ]


# ---------- Dashboard summary ----------
@router.get("/dashboard")
async def dashboard(user: User = Depends(require_user), db: Session = Depends(get_db)):
    pred_count = db.query(PredictionRecord).filter(PredictionRecord.user_id == user.id).count()
    chat_count = db.query(Conversation).filter(Conversation.user_id == user.id).count()
    nut_count = db.query(NutritionLog).filter(NutritionLog.user_id == user.id).count()
    recent = (
        db.query(PredictionRecord)
        .filter(PredictionRecord.user_id == user.id)
        .order_by(PredictionRecord.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "user": {
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role,
            "bmi_ready": bool(user.weight_kg and user.height_cm),
        },
        "stats": {
            "predictions": pred_count,
            "conversations": chat_count,
            "nutrition_logs": nut_count,
        },
        "recent_predictions": [
            {
                "id": r.id,
                "top_disease": r.top_disease,
                "top_confidence": r.top_confidence,
                "symptoms": r.symptoms,
                "created_at": r.created_at.isoformat(),
            }
            for r in recent
        ],
    }


# ---------- Model metrics ----------
@router.get("/metrics/model")
async def model_metrics():
    """Return last training evaluation metrics (educational synthetic data)."""
    from pathlib import Path
    import json
    path = Path(__file__).resolve().parents[3] / "models" / "metrics_v3.json"
    if not path.exists():
        path = Path(__file__).resolve().parents[2].parent / "models" / "metrics_v3.json"
    if path.exists():
        return json.loads(path.read_text())
    return {"error": "metrics not found — run scripts/train_and_evaluate.py"}


@router.get("/knowledge/disease/{name}")
async def disease_detail(name: str):
    """Structured educational disease knowledge (risk factors, red flags, specialist)."""
    from app.ml.disease_knowledge import get_disease_knowledge
    info = get_disease_knowledge(name)
    if not info:
        # try partial match
        from app.ml.disease_knowledge import DISEASE_STRUCTURED
        for k, v in DISEASE_STRUCTURED.items():
            if name.lower() in k.lower():
                return {"disease": k, **v, "disclaimer": "Educational only — not a clinical guideline."}
        raise HTTPException(status_code=404, detail="Disease knowledge not found")
    return {"disease": name, **info, "disclaimer": "Educational only — not a clinical guideline."}


# ---------- Voice / Multimodal scan ----------
@router.post("/voice/scan", response_model=VoiceScanResponse, dependencies=[Depends(rate_limit_dependency)])
async def voice_scan(
    body: VoiceScanRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    from app.services.voice_scan import VoiceScanService
    svc = VoiceScanService()
    mode = body.mode or (user.role if user else "patient")
    result = svc.process_transcript(
        transcript=body.transcript,
        db=db,
        mode=mode,
        consent_given=body.consent_given,
        audio_quality=body.audio_quality,
    )
    # persist prediction if logged in and predictions present
    if user and result.get("ok") and result.get("predictions"):
        rec = PredictionRecord(
            user_id=user.id,
            symptoms=result.get("detected_symptoms") or ["voice_input"],
            results=result.get("predictions"),
            top_disease=result["predictions"][0]["disease"] if result.get("predictions") else None,
            top_confidence=result["predictions"][0].get("confidence") if result.get("predictions") else None,
            mode=mode,
            safety_risk=(result.get("safety") or {}).get("risk_level"),
            model_version="voice-scan-v1",
        )
        db.add(rec)
        db.commit()
    return VoiceScanResponse(**{k: v for k, v in result.items() if k in VoiceScanResponse.model_fields})


@router.post("/multimodal/scan", dependencies=[Depends(rate_limit_dependency)])
async def multimodal_scan(
    body: MultimodalScanRequest,
    db: Session = Depends(get_db),
    user: Optional[User] = Depends(get_current_user),
):
    """
    Accepts user description + client-side quality metadata for an image/document.
    Does NOT run computer-vision disease diagnosis on pixels in this build.
    Routes text description through safety + knowledge pipeline.
    """
    if not body.consent_given:
        return {"ok": False, "error": "Consent required for multimodal capture.", "code": "CONSENT_REQUIRED"}
    quality_notes = []
    if body.quality:
        if body.quality.get("blur", 0) > 0.6:
            quality_notes.append("Image may be blurry — results uncertain.")
        if body.quality.get("lighting", 1) < 0.3:
            quality_notes.append("Poor lighting reported.")
    from app.services.chatbot import ChatbotService
    mode = body.mode or (user.role if user else "patient")
    prefix = f"[Multimodal {body.modality}] "
    result = ChatbotService().chat(prefix + body.description, db=db, mode=mode)
    return {
        "ok": True,
        "modality": body.modality,
        "quality_notes": quality_notes,
        **result,
        "disclaimer": (
            "This build analyzes your text description, not raw image pixels for diagnosis. "
            "Educational only — consult a clinician for visual findings."
        ),
    }
