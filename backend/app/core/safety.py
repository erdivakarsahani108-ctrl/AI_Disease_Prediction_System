"""Medical safety gates — mandatory pipeline components."""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from app.core.config import get_settings

settings = get_settings()


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class UserMode(str, Enum):
    PATIENT = "patient"
    STUDENT = "student"
    CLINICIAN = "clinician"
    ADMIN = "admin"


@dataclass
class SafetyResult:
    is_safe: bool
    risk_level: RiskLevel
    emergency_detected: bool
    blocked_reason: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    requires_escalation: bool = False
    disclaimer: str = (
        "This is not a medical diagnosis. Consult a qualified healthcare professional. "
        "For emergencies call local emergency services immediately."
    )


# Expanded emergency patterns (EN + HI + Hinglish)
EMERGENCY_PATTERNS = [
    r"\b(chest\s*pain|heart\s*attack|cardiac\s*arrest)\b",
    r"\b(stroke|brain\s*attack|sudden\s*weakness|face\s*droop)\b",
    r"\b(suicid|kill\s*myself|end\s*my\s*life|self[\s-]?harm)\b",
    r"\b(can'?t\s*breathe|difficulty\s*breathing|severe\s*shortness)\b",
    r"\b(unconscious|not\s*responding|passed\s*out)\b",
    r"\b(heavy\s*bleeding|bleeding\s*heavily|hemorrhage)\b",
    r"\b(seizure|convulsion|fit)\b",
    r"\b(anaphyla|severe\s*allergic|throat\s*swelling)\b",
    r"\b(छाती\s*में\s*दर्द|दिल\s*का\s*दौरा|हृदय\s*घात)\b",
    r"\b(स्ट्रोक|लकवा|अचानक\s*कमजोरी)\b",
    r"\b(आत्महत्या|खुदकुशी|जान\s*दे\s*दूं)\b",
    r"\b(सांस\s*नहीं|साँस\s*फूल|सांस\s*रुक)\b",
    r"\b(बेहोश|होश\s*नहीं|गिर\s*गया)\b",
    r"\b(तेज\s*खून\s*बह|बहुत\s*खून)\b",
    r"\b(dawai\s*zyada|overdose|poison)\b",
    r"\b(hemoptysis|coughing\s*blood|khoon\s*ki\s*khansi)\b",
    r"\b(suicidal|self[\s-]?harm|marna\s*chahta|jaan\s*de)\b",
    r"\b(blue\s*lips|cyanosis|neele\s*hoth)\b",
    r"\b(severe\s*abdominal\s*pain|tezz\s*pet\s*dard)\b",
    r"\b(pregnancy.*bleeding|pregnant.*pain|गर्भावस्था)\b",

]


def detect_emergency(text: str) -> bool:
    lowered = text.lower()
    for pattern in EMERGENCY_PATTERNS:
        if re.search(pattern, lowered, re.IGNORECASE):
            return True
    for kw in settings.EMERGENCY_KEYWORDS:
        if kw.lower() in lowered:
            return True
    return False


def run_safety_pipeline(
    text: str,
    mode: UserMode = UserMode.PATIENT,
    prediction_confidence: Optional[float] = None,
) -> SafetyResult:
    """
    Mandatory safety pipeline entry point.
    Always call before returning any medical content.
    """
    warnings: List[str] = []
    risk = RiskLevel.LOW
    emergency = detect_emergency(text)

    if emergency:
        return SafetyResult(
            is_safe=False,
            risk_level=RiskLevel.EMERGENCY,
            emergency_detected=True,
            blocked_reason="Potential medical emergency detected",
            warnings=[
                "🚨 EMERGENCY SIGNS DETECTED",
                "Please seek immediate medical help / call emergency services.",
                "Do not wait for AI advice in life-threatening situations.",
            ],
            requires_escalation=True,
            disclaimer=(
                "🚨 EMERGENCY: Call your local emergency number immediately. "
                "This system cannot provide emergency care."
            ),
        )

    # Confidence-based warnings
    if prediction_confidence is not None:
        if prediction_confidence < 0.35:
            risk = RiskLevel.HIGH
            warnings.append("Low model confidence — results are highly uncertain.")
            warnings.append("Please consult a doctor for proper evaluation.")
        elif prediction_confidence < 0.55:
            risk = RiskLevel.MEDIUM
            warnings.append("Moderate confidence — treat as decision support only.")

    # Mode-specific restrictions
    if mode == UserMode.PATIENT:
        warnings.append(
            "Patient mode: Information is general. A doctor must confirm any diagnosis."
        )
    elif mode == UserMode.STUDENT:
        warnings.append(
            "Student/Study mode: Educational content. Not for clinical decision making."
        )

    # Always attach core disclaimer
    warnings.append(
        "Never self-medicate based on AI output. Verify with licensed practitioners."
    )

    return SafetyResult(
        is_safe=True,
        risk_level=risk,
        emergency_detected=False,
        warnings=warnings,
        requires_escalation=risk in (RiskLevel.HIGH, RiskLevel.CRITICAL),
    )


def sanitize_output(text: str) -> str:
    """Remove any residual chain-of-thought or internal markers."""
    # Strip common CoT markers if present
    text = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"```(?:reasoning|thought|internal).*?```", "", text, flags=re.DOTALL)
    return text.strip()
