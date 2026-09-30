"""
Structured educational disease knowledge:
risk factors, red flags, specialist mapping, prevention, follow-up.
Synthetic/educational only — not clinical guidelines.
"""
from __future__ import annotations
from typing import Any, Dict, List, Optional

# ICD-like educational codes (NOT official ICD-10 licensing)
DISEASE_STRUCTURED: Dict[str, Dict[str, Any]] = {
    "Common Cold": {
        "code": "EDU-J00",
        "system": "allopathy",
        "risk_factors": ["close contact", "winter season", "weakened immunity"],
        "red_flags": ["high fever >3 days", "severe shortness of breath", "chest pain"],
        "specialist": "General Physician",
        "prevention": ["hand hygiene", "avoid close contact when sick"],
        "follow_up": "If symptoms worsen or last >10 days, see a doctor.",
        "tests": ["Usually clinical diagnosis; tests if complications suspected"],
    },
    "Influenza (Flu)": {
        "code": "EDU-J11",
        "system": "allopathy",
        "risk_factors": ["elderly", "pregnancy", "chronic disease", "crowded settings"],
        "red_flags": ["difficulty breathing", "confusion", "persistent high fever", "chest pain"],
        "specialist": "General Physician / Internist",
        "prevention": ["annual flu vaccination where recommended", "hand hygiene"],
        "follow_up": "Seek care early if high-risk group.",
        "tests": ["Rapid influenza test where available"],
    },
    "Type 2 Diabetes (risk indicators)": {
        "code": "EDU-E11",
        "system": "allopathy",
        "risk_factors": ["overweight", "family history", "sedentary lifestyle", "age >45"],
        "red_flags": ["very high glucose symptoms", "confusion", "vomiting with high sugar"],
        "specialist": "Endocrinologist / Internist",
        "prevention": ["healthy weight", "physical activity", "balanced diet"],
        "follow_up": "Lab confirmation (HbA1c, fasting glucose) required — not AI diagnosis.",
        "tests": ["Fasting glucose", "HbA1c", "OGTT"],
    },
    "Hypertension (risk indicators)": {
        "code": "EDU-I10",
        "system": "allopathy",
        "risk_factors": ["high salt intake", "obesity", "family history", "stress", "smoking"],
        "red_flags": ["severe headache with vision change", "chest pain", "neurological deficit"],
        "specialist": "Cardiologist / Internist",
        "prevention": ["reduce salt", "exercise", "weight management", "limit alcohol"],
        "follow_up": "Confirm with repeated BP measurements by clinician.",
        "tests": ["Office BP", "Home BP log", "basic metabolic panel"],
    },
    "PCOS (possible indicators)": {
        "code": "EDU-E28",
        "system": "allopathy",
        "risk_factors": ["family history", "insulin resistance", "obesity"],
        "red_flags": ["very prolonged absence of periods", "severe pelvic pain"],
        "specialist": "Gynecologist / Endocrinologist",
        "prevention": ["lifestyle measures under guidance"],
        "follow_up": "Clinical evaluation + labs/ultrasound as indicated by doctor.",
        "tests": ["Hormonal panel", "Pelvic ultrasound (as ordered)"],
    },
    "Dengue (suspected)": {
        "code": "EDU-A90",
        "system": "allopathy",
        "risk_factors": ["mosquito exposure", "endemic area", "monsoon season"],
        "red_flags": ["bleeding", "severe abdominal pain", "persistent vomiting", "lethargy", "plasma leakage signs"],
        "specialist": "Physician / Infectious disease (hospital if severe)",
        "prevention": ["mosquito control", "repellents", "eliminate breeding sites"],
        "follow_up": "Urgent medical evaluation; monitor platelets if confirmed.",
        "tests": ["NS1 antigen", "IgM/IgG", "CBC with platelets"],
    },
    "Tuberculosis (possible)": {
        "code": "EDU-A15",
        "system": "allopathy",
        "risk_factors": ["close contact with TB", "immunocompromised", "malnutrition"],
        "red_flags": ["hemoptysis", "severe weight loss", "night sweats with prolonged cough"],
        "specialist": "Pulmonologist / TB clinic",
        "prevention": ["infection control", "treatment of latent TB where indicated"],
        "follow_up": "Never self-treat; requires public health protocols.",
        "tests": ["Sputum AFB/GeneXpert", "Chest X-ray"],
    },
    "Anxiety Disorder (possible)": {
        "code": "EDU-F41",
        "system": "allopathy",
        "risk_factors": ["stress", "trauma history", "substance use", "family history"],
        "red_flags": ["suicidal thoughts", "inability to function", "panic with chest pain (rule out cardiac)"],
        "specialist": "Psychiatrist / Clinical psychologist",
        "prevention": ["stress management", "sleep hygiene", "social support"],
        "follow_up": "Professional mental health evaluation recommended.",
        "tests": ["Clinical assessment; rule out medical causes as needed"],
    },
    "Bronchial Asthma (possible)": {
        "code": "EDU-J45",
        "system": "allopathy",
        "risk_factors": ["allergies", "family history", "smoking exposure", "pollution"],
        "red_flags": ["severe breathlessness", "unable to speak full sentences", "blue lips", "silent chest"],
        "specialist": "Pulmonologist / Allergist",
        "prevention": ["avoid triggers", "controller meds as prescribed"],
        "follow_up": "Asthma action plan with clinician.",
        "tests": ["Spirometry", "Peak flow"],
    },
    "Urinary Tract Infection": {
        "code": "EDU-N39",
        "system": "allopathy",
        "risk_factors": ["female sex", "catheter use", "diabetes", "sexual activity"],
        "red_flags": ["flank pain with fever", "confusion (elderly)", "vomiting"],
        "specialist": "General Physician / Urologist if recurrent",
        "prevention": ["hydration", "hygiene"],
        "follow_up": "Culture if recurrent or complicated.",
        "tests": ["Urinalysis", "Urine culture"],
    },
}


def get_disease_knowledge(name: str) -> Optional[Dict[str, Any]]:
    return DISEASE_STRUCTURED.get(name)


def search_by_red_flag(text: str) -> List[str]:
    t = text.lower()
    hits = []
    for disease, info in DISEASE_STRUCTURED.items():
        for rf in info.get("red_flags", []):
            if any(w in t for w in rf.lower().split() if len(w) > 3):
                hits.append(disease)
                break
    return hits
