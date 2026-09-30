"""Basic tests for disease predictor."""
from app.ml.predictor import get_predictor


def test_cold_symptoms():
    p = get_predictor()
    results = p.predict(["runny_nose", "sneezing", "sore_throat", "cough"])
    assert len(results) > 0
    assert any("Cold" in r["disease"] or "Flu" in r["disease"] or "Rhinitis" in r["disease"] for r in results)


def test_empty():
    p = get_predictor()
    assert p.predict([]) == []


def test_hindi_alias():
    p = get_predictor()
    results = p.predict(["bukhar", "khansi", "thakaan"])
    assert len(results) > 0
