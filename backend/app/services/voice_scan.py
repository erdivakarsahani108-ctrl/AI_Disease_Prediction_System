"""
Voice / multimodal disease-scan support layer.
Accepts transcribed text (from client Web Speech API or uploaded audio transcript).
Runs existing safety + symptom extraction + prediction pipeline.
Does NOT claim acoustic pathology diagnosis from raw audio waveforms.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.core.safety import UserMode, run_safety_pipeline
from app.ml.predictor import get_predictor
from app.services.language import detect_language, get_language_name
from app.services.chatbot import ChatbotService


class VoiceScanService:
    def __init__(self):
        self.predictor = get_predictor()
        self.chatbot = ChatbotService()

    def process_transcript(
        self,
        transcript: str,
        db: Session,
        mode: str = "patient",
        consent_given: bool = False,
        audio_quality: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        if not consent_given:
            return {
                "ok": False,
                "error": "Microphone/voice processing requires explicit user consent.",
                "code": "CONSENT_REQUIRED",
            }

        transcript = (transcript or "").strip()
        if len(transcript) < 2:
            return {
                "ok": False,
                "error": "Transcript too short or empty. Please speak clearly and retry.",
                "code": "LOW_QUALITY",
            }

        quality_notes: List[str] = []
        if audio_quality:
            if audio_quality.get("noise_level", 0) > 0.7:
                quality_notes.append("High background noise reported — confidence may be reduced.")
            if audio_quality.get("duration_sec", 10) < 1.5:
                quality_notes.append("Very short capture — may miss symptoms.")

        mode_enum = UserMode(mode) if mode in UserMode._value2member_map_ else UserMode.PATIENT
        safety = run_safety_pipeline(transcript, mode=mode_enum)
        if safety.emergency_detected:
            return {
                "ok": True,
                "emergency": True,
                "reply": safety.disclaimer,
                "safety": {
                    "risk_level": safety.risk_level.value,
                    "warnings": safety.warnings,
                    "emergency": True,
                },
                "transcript": transcript,
                "quality_notes": quality_notes,
                "disclaimer": safety.disclaimer,
            }

        # Reuse chatbot pipeline for symptom extraction + RAG
        chat_result = self.chatbot.chat(transcript, db=db, mode=mode)
        predictions = chat_result.get("predictions") or []
        if not predictions and chat_result.get("detected_symptoms"):
            predictions = self.predictor.predict(chat_result["detected_symptoms"], top_k=5)

        return {
            "ok": True,
            "emergency": False,
            "transcript": transcript,
            "language": chat_result.get("language"),
            "language_name": chat_result.get("language_name"),
            "detected_symptoms": chat_result.get("detected_symptoms", []),
            "predictions": predictions,
            "citations": chat_result.get("citations", []),
            "reply": chat_result.get("reply"),
            "safety": chat_result.get("safety"),
            "quality_notes": quality_notes,
            "modality": "voice_transcript",
            "disclaimer": (
                "Voice input is converted to text then analyzed. "
                "This is NOT acoustic medical diagnosis from sound patterns. "
                "Educational decision support only."
            ),
        }
