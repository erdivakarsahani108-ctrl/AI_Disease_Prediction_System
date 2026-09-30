"""
Disease prediction engine v2.
Hybrid: rule-based Jaccard + RandomForest trained on expanded educational mappings.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder

from app.ml.disease_data import (
    DISEASE_NOTES,
    DISEASE_SYMPTOMS,
    SYMPTOM_ALIASES,
    SYMPTOM_LIST,
)


class DiseasePredictor:
    MODEL_VERSION = "hybrid-rf-v3"

    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or Path(__file__).resolve().parents[3] / "models"
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.mlb: Optional[MultiLabelBinarizer] = None
        self.label_encoder: Optional[LabelEncoder] = None
        self.clf: Optional[RandomForestClassifier] = None
        self._train_or_load()

    def _normalize_symptom(self, s: str) -> str:
        s = s.strip().lower().replace("-", "_").replace(" ", "_")
        for alias, canonical in SYMPTOM_ALIASES.items():
            if alias.replace(" ", "_") in s or s in alias.replace(" ", "_") or alias in s:
                return canonical
        for known in SYMPTOM_LIST:
            if known in s or s in known:
                return known
        return s

    def _train_or_load(self) -> None:
        model_path = self.model_dir / "disease_rf_v3.joblib"
        mlb_path = self.model_dir / "mlb_v3.joblib"
        le_path = self.model_dir / "label_encoder_v3.joblib"

        if model_path.exists() and mlb_path.exists() and le_path.exists():
            self.clf = joblib.load(model_path)
            self.mlb = joblib.load(mlb_path)
            self.label_encoder = joblib.load(le_path)
            return
        # fallback older artifacts
        for ver in ("v2", "v1"):
            mp = self.model_dir / f"disease_rf_{ver}.joblib"
            if mp.exists():
                self.clf = joblib.load(mp)
                self.mlb = joblib.load(self.model_dir / f"mlb_{ver}.joblib")
                self.label_encoder = joblib.load(self.model_dir / f"label_encoder_{ver}.joblib")
                return

        X_raw: List[List[str]] = []
        y_raw: List[str] = []
        for disease, symptoms in DISEASE_SYMPTOMS.items():
            cleaned = [s for s in symptoms if s in SYMPTOM_LIST]
            if not cleaned:
                continue
            X_raw.append(cleaned)
            y_raw.append(disease)
            if len(cleaned) > 3:
                X_raw.append(cleaned[:-1])
                y_raw.append(disease)
                X_raw.append(cleaned[1:])
                y_raw.append(disease)
            if len(cleaned) > 4:
                X_raw.append(cleaned[::2])
                y_raw.append(disease)

        self.mlb = MultiLabelBinarizer(classes=SYMPTOM_LIST)
        X = self.mlb.fit_transform(X_raw)
        self.label_encoder = LabelEncoder()
        y = self.label_encoder.fit_transform(y_raw)

        self.clf = RandomForestClassifier(
            n_estimators=120,
            max_depth=14,
            min_samples_leaf=1,
            random_state=42,
            class_weight="balanced_subsample",
            n_jobs=-1,
        )
        self.clf.fit(X, y)

        joblib.dump(self.clf, model_path)
        joblib.dump(self.mlb, mlb_path)
        joblib.dump(self.label_encoder, le_path)

    def predict(self, symptoms: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        if not symptoms:
            return []

        normalized = [self._normalize_symptom(s) for s in symptoms]
        normalized = list(dict.fromkeys(
            s for s in normalized if s in SYMPTOM_LIST or s in SYMPTOM_ALIASES.values()
        ))
        if not normalized:
            return self._rule_based(symptoms, top_k)

        X = self.mlb.transform([normalized])
        proba = self.clf.predict_proba(X)[0]
        classes = self.label_encoder.classes_

        ranked = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)[:top_k]
        results = []
        for disease, conf in ranked:
            matching = sorted(set(DISEASE_SYMPTOMS.get(disease, [])) & set(normalized))
            note = DISEASE_NOTES.get(disease, "")
            results.append({
                "disease": disease,
                "confidence": round(float(conf), 4),
                "matching_symptoms": matching,
                "total_typical_symptoms": len(DISEASE_SYMPTOMS.get(disease, [])),
                "note": note,
                "explanation": (
                    f"Matched {len(matching)}/{len(DISEASE_SYMPTOMS.get(disease, []))} "
                    f"typical features. Model confidence is not clinical probability."
                ),
            })

        rule = self._rule_based(normalized, top_k)
        return self._merge(results, rule, top_k)

    def _rule_based(self, symptoms: List[str], top_k: int) -> List[Dict[str, Any]]:
        scores: List[Tuple[str, float, List[str]]] = []
        norm = set(self._normalize_symptom(s) for s in symptoms)
        for disease, typical in DISEASE_SYMPTOMS.items():
            typical_set = set(s for s in typical if s in SYMPTOM_LIST)
            inter = norm & typical_set
            if not inter:
                continue
            score = len(inter) / (len(typical_set) + 0.4)
            scores.append((disease, min(score, 0.95), sorted(inter)))
        scores.sort(key=lambda x: x[1], reverse=True)
        out = []
        for d, s, m in scores[:top_k]:
            out.append({
                "disease": d,
                "confidence": round(s, 4),
                "matching_symptoms": m,
                "total_typical_symptoms": len(DISEASE_SYMPTOMS[d]),
                "note": DISEASE_NOTES.get(d, ""),
                "explanation": f"Rule-based overlap: {len(m)} symptoms.",
            })
        return out

    def _merge(self, ml: List[Dict], rule: List[Dict], top_k: int) -> List[Dict]:
        combined: Dict[str, Dict] = {}
        for r in ml + rule:
            name = r["disease"]
            if name not in combined:
                combined[name] = r
            else:
                combined[name]["confidence"] = round(
                    (combined[name]["confidence"] + r["confidence"]) / 2, 4
                )
                combined[name]["matching_symptoms"] = sorted(
                    set(combined[name]["matching_symptoms"]) | set(r["matching_symptoms"])
                )
        return sorted(combined.values(), key=lambda x: x["confidence"], reverse=True)[:top_k]


_predictor: Optional[DiseasePredictor] = None


def get_predictor() -> DiseasePredictor:
    global _predictor
    if _predictor is None:
        _predictor = DiseasePredictor()
    return _predictor
