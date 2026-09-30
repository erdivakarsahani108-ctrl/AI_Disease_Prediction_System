
from __future__ import annotations
import hashlib
from typing import Any, Dict, List

HIGH_RISK_MODALITIES={"pathology","eye_image","skin_image","lab_report","prescription"}

def quality_gate(modality: str, quality: Dict[str,Any])->List[str]:
    notes=[]
    if quality.get("blur_score") is not None and quality["blur_score"] < 0.45:
        notes.append("Image/document may be too blurry for reliable extraction.")
    if quality.get("lighting_score") is not None and quality["lighting_score"] < 0.40:
        notes.append("Lighting/contrast may be insufficient.")
    if quality.get("completeness") is not None and quality["completeness"] < 0.70:
        notes.append("Input appears incomplete.")
    if modality in HIGH_RISK_MODALITIES:
        notes.append("High-risk modality: output requires professional review and must not be treated as a diagnosis.")
    return notes

def analyze_description(modality:str, description:str, quality:Dict[str,Any])->Dict[str,Any]:
    notes=quality_gate(modality,quality)
    # Conservative extraction only: no invented pathology or disease.
    return {
        "modality": modality,
        "input_hash": hashlib.sha256(description.encode()).hexdigest(),
        "quality_notes": notes,
        "findings": [],
        "requires_human_review": modality in HIGH_RISK_MODALITIES,
        "diagnosis_claim": False,
        "disclaimer": "This scan pipeline extracts/organizes information; it does not establish a medical diagnosis."
    }
