"""Core unit tests — run: PYTHONPATH=. pytest tests/ -q"""
from app.ml.predictor import get_predictor
from app.ml.disease_data import DISEASE_SYMPTOMS
from app.ml.disease_knowledge import DISEASE_STRUCTURED, get_disease_knowledge
from app.services.nutrition import calc_bmi, calc_bmr, full_nutrition_profile
from app.core.safety import detect_emergency, run_safety_pipeline, UserMode
from app.services.language import detect_language


def test_disease_count():
    assert len(DISEASE_SYMPTOMS) >= 35


def test_predictor_flu_like():
    p = get_predictor()
    r = p.predict(["fever", "cough", "body_ache", "chills", "fatigue"])
    assert len(r) >= 1
    assert 0 <= r[0]["confidence"] <= 1


def test_bmi():
    r = calc_bmi(70, 170)
    assert 24 < r["bmi"] < 25
    assert r["category"] == "Normal"


def test_bmr():
    bmr = calc_bmr(70, 170, 30, "male")
    assert 1500 < bmr < 1800


def test_nutrition_profile():
    p = full_nutrition_profile(70, 170, 30, "female", "moderate", "lose", ["diabetes"], ["peanuts"])
    assert p["calorie_target"] > 0
    assert any("diabetes" in t.lower() or "glycemic" in t.lower() for t in p["general_tips"])


def test_emergency_detection():
    assert detect_emergency("I have severe chest pain and can't breathe")
    assert not detect_emergency("I have a mild headache")


def test_safety_pipeline():
    s = run_safety_pipeline("fever and cough", mode=UserMode.PATIENT, prediction_confidence=0.3)
    assert s.risk_level.value in ("low", "medium", "high", "critical", "emergency")


def test_language_hinglish():
    assert detect_language("mujhe bukhar aur khansi hai") in ("hinglish", "hi", "en")


def test_disease_knowledge():
    k = get_disease_knowledge("Dengue (suspected)")
    assert k is not None
    assert "red_flags" in k
    assert len(DISEASE_STRUCTURED) >= 8
