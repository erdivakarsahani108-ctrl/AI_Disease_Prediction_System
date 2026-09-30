"""
Expanded educational disease–symptom knowledge.
Synthetic / public-domain style mappings for demo & education.
NOT clinical diagnostic probabilities.
"""
from __future__ import annotations
from typing import Dict, List

SYMPTOM_LIST = [
    "fever", "mild_fever", "high_fever", "cough", "dry_cough", "wet_cough",
    "fatigue", "headache", "sore_throat", "runny_nose", "body_ache", "chills",
    "nausea", "vomiting", "diarrhea", "abdominal_pain", "chest_pain",
    "shortness_of_breath", "dizziness", "rash", "itching", "joint_pain",
    "back_pain", "loss_of_appetite", "weight_loss", "night_sweats",
    "frequent_urination", "excessive_thirst", "blurred_vision", "swelling",
    "constipation", "heartburn", "anxiety", "insomnia", "palpitations",
    "sneezing", "watery_eyes", "ear_pain", "neck_stiffness", "photophobia",
    "yellow_skin", "dark_urine", "blood_in_stool", "blood_in_urine", "red_eyes",
    "muscle_pain", "weakness", "sweating", "confusion", "stiff_neck",
    "loss_of_smell", "loss_of_taste", "wheezing", "hoarseness",
    "painful_urination", "lower_abdominal_pain", "irregular_periods",
    "hair_loss", "acne", "weight_gain", "cold_intolerance", "heat_intolerance",
    "tremor", "numbness", "tingling", "memory_issues", "depression_mood",
]

SYMPTOM_ALIASES: Dict[str, str] = {
    "bukhar": "fever", "tap": "fever", "jwar": "fever", "tezz bukhar": "high_fever",
    "khansi": "cough", "kansi": "cough", "sukhi khansi": "dry_cough",
    "thakaan": "fatigue", "thakan": "fatigue", "kamjori": "fatigue", "weakness": "weakness",
    "sir dard": "headache", "sirdard": "headache", "matha dard": "headache",
    "gale mein dard": "sore_throat", "gala kharab": "sore_throat",
    "nak se pani": "runny_nose", "zukam": "runny_nose",
    "badan dard": "body_ache", "joron ka dard": "joint_pain", "muscle pain": "muscle_pain",
    "ulti": "vomiting", "qai": "vomiting",
    "dast": "diarrhea", "pet kharab": "diarrhea",
    "pet dard": "abdominal_pain", "pet mein dard": "abdominal_pain",
    "saans phoolna": "shortness_of_breath", "saans ki takleef": "shortness_of_breath",
    "chakkar": "dizziness", "ghabrahat": "anxiety",
    "neend na aana": "insomnia", "khujli": "itching",
    "daane": "rash", "lal pani": "rash",
    "pisab mein jalan": "painful_urination", "bar bar pisab": "frequent_urination",
    "zyada pyas": "excessive_thirst", "weight kam": "weight_loss",
    "weight badhna": "weight_gain", "baal jhadna": "hair_loss",
}

# disease → typical symptoms (educational mapping, 40+ conditions)
DISEASE_SYMPTOMS: Dict[str, List[str]] = {
    "Common Cold": ["runny_nose", "sneezing", "sore_throat", "cough", "mild_fever", "fatigue"],
    "Influenza (Flu)": ["fever", "high_fever", "cough", "body_ache", "fatigue", "chills", "headache", "sore_throat"],
    "COVID-19 (suspected)": ["fever", "dry_cough", "fatigue", "shortness_of_breath", "loss_of_smell", "loss_of_taste", "body_ache"],
    "Migraine": ["headache", "nausea", "photophobia", "dizziness", "fatigue", "vomiting"],
    "Tension Headache": ["headache", "neck_stiffness", "fatigue", "anxiety"],
    "Gastroenteritis": ["nausea", "vomiting", "diarrhea", "abdominal_pain", "fever", "fatigue", "loss_of_appetite"],
    "Acid Reflux / GERD": ["heartburn", "abdominal_pain", "nausea", "chest_pain", "hoarseness"],
    "Urinary Tract Infection": ["frequent_urination", "painful_urination", "lower_abdominal_pain", "fever", "fatigue"],
    "Type 2 Diabetes (risk indicators)": ["frequent_urination", "excessive_thirst", "fatigue", "blurred_vision", "weight_loss", "slow_healing"],
    "Allergic Rhinitis": ["sneezing", "runny_nose", "watery_eyes", "itching", "fatigue"],
    "Bronchial Asthma (possible)": ["shortness_of_breath", "wheezing", "cough", "chest_pain", "fatigue"],
    "Anemia (possible)": ["fatigue", "dizziness", "shortness_of_breath", "palpitations", "weakness", "loss_of_appetite"],
    "Anxiety Disorder (possible)": ["anxiety", "palpitations", "insomnia", "fatigue", "dizziness", "sweating"],
    "Hypertension (risk indicators)": ["headache", "dizziness", "palpitations", "fatigue", "chest_pain", "blurred_vision"],
    "Dengue (suspected)": ["high_fever", "body_ache", "headache", "rash", "fatigue", "nausea", "joint_pain", "muscle_pain"],
    "Malaria (suspected)": ["high_fever", "chills", "headache", "body_ache", "fatigue", "nausea", "vomiting", "sweating"],
    "Typhoid (suspected)": ["fever", "high_fever", "abdominal_pain", "headache", "fatigue", "loss_of_appetite", "constipation", "diarrhea"],
    "Chickenpox": ["fever", "rash", "itching", "fatigue", "body_ache", "loss_of_appetite"],
    "Measles": ["fever", "cough", "runny_nose", "rash", "red_eyes", "fatigue"],
    "Tuberculosis (possible)": ["cough", "wet_cough", "fever", "night_sweats", "weight_loss", "fatigue", "loss_of_appetite"],
    "Pneumonia (possible)": ["fever", "cough", "shortness_of_breath", "chest_pain", "fatigue", "chills"],
    "Bronchitis": ["cough", "wet_cough", "fatigue", "chest_pain", "mild_fever", "shortness_of_breath"],
    "Sinusitis": ["headache", "runny_nose", "facial_pain", "fatigue", "cough", "sore_throat"],
    "Conjunctivitis": ["red_eyes", "itching", "watery_eyes", "discharge"],
    "Hypothyroidism (possible)": ["fatigue", "weight_gain", "cold_intolerance", "hair_loss", "constipation", "depression_mood"],
    "Hyperthyroidism (possible)": ["weight_loss", "heat_intolerance", "palpitations", "tremor", "anxiety", "insomnia"],
    "PCOS (possible indicators)": ["irregular_periods", "weight_gain", "acne", "hair_loss", "fatigue"],
    "Irritable Bowel Syndrome": ["abdominal_pain", "diarrhea", "constipation", "bloating", "fatigue"],
    "Peptic Ulcer (possible)": ["abdominal_pain", "heartburn", "nausea", "loss_of_appetite", "vomiting"],
    "Kidney Stone (possible)": ["severe_flank_pain", "blood_in_urine", "nausea", "vomiting", "frequent_urination"],
    "Appendicitis (possible)": ["abdominal_pain", "lower_abdominal_pain", "nausea", "vomiting", "fever", "loss_of_appetite"],
    "Depression (possible)": ["depression_mood", "fatigue", "insomnia", "loss_of_appetite", "memory_issues", "weakness"],
    "Vertigo": ["dizziness", "nausea", "vomiting", "imbalance"],
    "Eczema / Dermatitis": ["rash", "itching", "dry_skin", "redness"],
    "Rheumatoid Arthritis (possible)": ["joint_pain", "swelling", "fatigue", "morning_stiffness", "weakness"],
    "Osteoarthritis (possible)": ["joint_pain", "stiffness", "swelling", "reduced_mobility"],
    "Food Poisoning": ["nausea", "vomiting", "diarrhea", "abdominal_pain", "fever", "weakness"],
    "Dehydration": ["dizziness", "fatigue", "dry_mouth", "dark_urine", "weakness", "confusion"],
    "Heat Exhaustion": ["sweating", "dizziness", "nausea", "weakness", "headache", "fatigue"],
    "Insomnia Disorder": ["insomnia", "fatigue", "anxiety", "irritability", "memory_issues"],
}

# Severity / escalation hints (educational)
DISEASE_NOTES: Dict[str, str] = {
    "Dengue (suspected)": "Seek medical care promptly; monitor platelet count if confirmed.",
    "Malaria (suspected)": "Urgent testing recommended in endemic areas.",
    "Typhoid (suspected)": "Medical evaluation and lab confirmation needed.",
    "Tuberculosis (possible)": "Requires clinical evaluation and sputum/chest imaging.",
    "Pneumonia (possible)": "Seek care if breathing difficulty or high fever.",
    "Appendicitis (possible)": "Urgent surgical evaluation if severe right lower pain.",
    "COVID-19 (suspected)": "Follow local testing and isolation guidelines.",
    "PCOS (possible indicators)": "Gynecologist/endocrinologist evaluation recommended.",
}
