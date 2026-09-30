"""
BMI, BMR, TDEE, macro targets & basic disease-aware diet guidance.
Educational formulas only — not personalized medical nutrition therapy.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def calc_bmi(weight_kg: float, height_cm: float) -> Dict[str, Any]:
    if height_cm <= 0 or weight_kg <= 0:
        raise ValueError("Invalid height or weight")
    h_m = height_cm / 100.0
    bmi = round(weight_kg / (h_m * h_m), 2)
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    return {"bmi": bmi, "category": category}


def calc_bmr(weight_kg: float, height_cm: float, age: int, sex: str) -> float:
    """Mifflin-St Jeor equation."""
    sex = (sex or "male").lower()
    if sex in ("female", "f", "woman"):
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    return round(bmr, 1)


def calc_tdee(bmr: float, activity: str = "moderate") -> float:
    mult = ACTIVITY_MULTIPLIERS.get(activity, 1.55)
    return round(bmr * mult, 1)


def calc_macros(
    tdee: float,
    goal: str = "maintain",
    weight_kg: float = 70,
) -> Dict[str, float]:
    """
    Simple macro split:
    - maintain: TDEE
    - lose: TDEE - 500
    - gain: TDEE + 300
    Protein ~1.6g/kg, fat 25-30%, rest carbs.
    """
    if goal == "lose":
        calories = max(tdee - 500, 1200)
    elif goal == "gain":
        calories = tdee + 300
    else:
        calories = tdee

    protein_g = round(weight_kg * 1.6, 1)
    fat_g = round((calories * 0.28) / 9, 1)
    protein_cal = protein_g * 4
    fat_cal = fat_g * 9
    carbs_g = round(max(calories - protein_cal - fat_cal, 0) / 4, 1)

    return {
        "calorie_target": round(calories, 0),
        "protein_g": protein_g,
        "carbs_g": carbs_g,
        "fat_g": fat_g,
    }


# Basic disease-aware guidance (educational, not prescription)
DISEASE_DIET_HINTS: Dict[str, List[str]] = {
    "diabetes": [
        "Prefer low glycemic index foods; control portion of refined carbs.",
        "Include fiber-rich vegetables, whole grains, legumes.",
        "Regular meal timing helps glucose stability.",
        "Consult a registered dietitian for personalized plan.",
    ],
    "hypertension": [
        "Reduce sodium (salt); DASH-style diet is commonly recommended.",
        "Increase fruits, vegetables, low-fat dairy, potassium-rich foods.",
        "Limit processed and packaged foods.",
    ],
    "pcos": [
        "Focus on balanced meals with adequate protein and fiber.",
        "Limit highly processed sugars; prefer whole foods.",
        "Weight management (if overweight) can improve symptoms — under guidance.",
    ],
    "gerd": [
        "Avoid large meals close to bedtime; elevate head if needed.",
        "Limit spicy, very fatty, citrus, caffeine if they trigger symptoms.",
    ],
    "anemia": [
        "Iron-rich foods (leafy greens, legumes, fortified cereals) + vitamin C.",
        "Discuss iron supplements only with a doctor after labs.",
    ],
    "thyroid": [
        "Ensure adequate iodine and selenium from balanced diet.",
        "Do not self-start high-dose supplements without medical advice.",
    ],
}


def diet_guidance(
    conditions: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
    goal: str = "maintain",
) -> Dict[str, Any]:
    tips: List[str] = [
        "Drink adequate water (roughly 30–35 ml/kg/day unless restricted).",
        "Prioritize whole foods over ultra-processed items.",
        "This is general educational guidance — not a therapeutic diet plan.",
    ]
    if conditions:
        for c in conditions:
            key = c.lower().replace(" ", "")
            for dk, hints in DISEASE_DIET_HINTS.items():
                if dk in key or key in dk:
                    tips.extend(hints)
    allergy_notes = []
    if allergies:
        allergy_notes = [f"Strictly avoid: {a}" for a in allergies]
        tips.append("Always read labels and inform caregivers about allergies.")

    return {
        "general_tips": list(dict.fromkeys(tips)),
        "allergy_notes": allergy_notes,
        "goal": goal,
    }


def full_nutrition_profile(
    weight_kg: float,
    height_cm: float,
    age: int,
    sex: str,
    activity: str = "moderate",
    goal: str = "maintain",
    conditions: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
) -> Dict[str, Any]:
    bmi_info = calc_bmi(weight_kg, height_cm)
    bmr = calc_bmr(weight_kg, height_cm, age, sex)
    tdee = calc_tdee(bmr, activity)
    macros = calc_macros(tdee, goal, weight_kg)
    guidance = diet_guidance(conditions, allergies, goal)
    return {
        **bmi_info,
        "bmr": bmr,
        "tdee": tdee,
        "activity_level": activity,
        **macros,
        **guidance,
        "disclaimer": (
            "BMI/BMR/TDEE are estimates using standard formulas. "
            "Not medical advice. Consult a doctor or registered dietitian."
        ),
    }
