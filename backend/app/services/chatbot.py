"""
Multilingual medical knowledge assistant v2.
Uses DB knowledge + RAG retrieval + ML prediction + safety pipeline.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.safety import UserMode, run_safety_pipeline, sanitize_output
from app.ml.predictor import get_predictor
from app.ml.disease_data import SYMPTOM_ALIASES
from app.services.language import detect_language, get_language_name, normalize_query
from app.services.rag import retrieve


class ChatbotService:
    def __init__(self):
        self.predictor = get_predictor()

    def _extract_symptoms(self, text: str) -> List[str]:
        found = []
        lowered = text.lower()
        for alias, canonical in SYMPTOM_ALIASES.items():
            if alias in lowered:
                found.append(canonical)
        for s in [
            "fever", "cough", "headache", "fatigue", "nausea", "vomiting",
            "diarrhea", "rash", "itching", "dizziness", "chest pain",
            "shortness of breath", "body ache", "sore throat", "anxiety",
            "insomnia", "joint pain", "weight loss", "weight gain",
        ]:
            if s in lowered or s.replace(" ", "_") in lowered:
                found.append(s.replace(" ", "_"))
        return list(dict.fromkeys(found))

    def _detect_intent(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["bmi", "bmr", "calorie", "diet", "nutrition", "weight", "protein"]):
            return "nutrition"
        if any(w in t for w in ["predict", "what disease", "kya bimari", "diagnosis", "symptoms se"]):
            return "predict"
        if any(w in t for w in ["emergency", "urgent", "help now", "aapatkal"]):
            return "emergency"
        return "general"

    def chat(
        self,
        message: str,
        db: Session,
        mode: str = "patient",
        medical_system: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        mode_enum = UserMode(mode) if mode in UserMode._value2member_map_ else UserMode.PATIENT

        safety = run_safety_pipeline(message, mode=mode_enum)
        if safety.emergency_detected:
            return {
                "reply": safety.disclaimer,
                "language": detect_language(message),
                "language_name": get_language_name(detect_language(message)),
                "intent": "emergency",
                "detected_symptoms": [],
                "predictions": [],
                "citations": [],
                "safety": {
                    "risk_level": safety.risk_level.value,
                    "emergency": True,
                    "warnings": safety.warnings,
                    "requires_escalation": True,
                },
                "mode": mode_enum.value,
                "medical_system": medical_system,
            }

        lang = detect_language(message)
        query = normalize_query(message, lang)
        intent = self._detect_intent(query)
        predictions: List[Dict] = []
        citations: List[Dict] = []
        reply_parts: List[str] = []

        symptoms = self._extract_symptoms(query)
        if symptoms or intent == "predict":
            if symptoms:
                predictions = self.predictor.predict(symptoms, top_k=4)
                conf = predictions[0]["confidence"] if predictions else 0.0
                safety = run_safety_pipeline(message, mode=mode_enum, prediction_confidence=conf)
                if lang in ("hi", "hinglish", "bhojpuri"):
                    reply_parts.append(
                        f"आपके बताए लक्षणों ({', '.join(symptoms)}) के आधार पर संभावित स्थितियाँ "
                        f"(यह निदान नहीं है):"
                    )
                else:
                    reply_parts.append(
                        f"Based on symptoms ({', '.join(symptoms)}), possible conditions "
                        f"(NOT a diagnosis):"
                    )
                for p in predictions:
                    line = (
                        f"• {p['disease']} — ~{p['confidence']*100:.0f}% "
                        f"(matched: {', '.join(p['matching_symptoms']) or 'partial'})"
                    )
                    if p.get("note"):
                        line += f"\n  Note: {p['note']}"
                    reply_parts.append(line)
            else:
                reply_parts.append(
                    "कृपया मुख्य लक्षण बताएँ।" if lang in ("hi", "hinglish")
                    else "Please describe your main symptoms."
                )

        # RAG retrieval from DB
        docs = retrieve(db, query, medical_system=medical_system, top_k=3, lang=lang)
        for d in docs:
            reply_parts.append(f"\n📚 {d['title']} ({d['medical_system']}):\n{d['content']}")
            citations.append({
                "id": d["id"],
                "title": d["title"],
                "system": d["medical_system"],
                "source": d["source"],
                "evidence_level": d["evidence_level"],
                "score": d["score"],
            })

        if not reply_parts:
            if lang in ("hi", "hinglish", "bhojpuri"):
                reply_parts.append(
                    "मैं शैक्षिक चिकित्सा सहायक हूँ। लक्षण या स्वास्थ्य प्रश्न पूछें। "
                    "मैं निदान नहीं करता — डॉक्टर से सलाह लें।"
                )
            else:
                reply_parts.append(
                    "I am an educational medical assistant. Describe symptoms or ask a health question. "
                    "I do not diagnose — consult a doctor."
                )

        reply_parts.append("\n⚠️ " + safety.disclaimer)
        full_reply = sanitize_output("\n".join(reply_parts))

        return {
            "reply": full_reply,
            "language": lang,
            "language_name": get_language_name(lang),
            "intent": intent,
            "detected_symptoms": symptoms,
            "predictions": predictions,
            "citations": citations,
            "safety": {
                "risk_level": safety.risk_level.value,
                "emergency": safety.emergency_detected,
                "warnings": safety.warnings,
                "requires_escalation": safety.requires_escalation,
            },
            "mode": mode_enum.value,
            "medical_system": medical_system,
        }
