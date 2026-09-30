#!/usr/bin/env python3
"""
Train + evaluate disease prediction model on educational dataset.
Produces accuracy, precision, recall, F1, classification report, confusion matrix summary.
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import LabelEncoder, MultiLabelBinarizer

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from app.ml.disease_data import SYMPTOM_LIST  # noqa: E402

DATA = ROOT / "data" / "symptom_disease_dataset.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)


def load_split(split: str):
    import csv
    X, y = [], []
    with DATA.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["split"] != split:
                continue
            symptoms = [s for s in row["symptoms"].split("|") if s in SYMPTOM_LIST]
            if not symptoms:
                continue
            X.append(symptoms)
            y.append(row["disease"])
    return X, y


def main():
    X_train, y_train = load_split("train")
    X_val, y_val = load_split("val")
    X_test, y_test = load_split("test")

    mlb = MultiLabelBinarizer(classes=SYMPTOM_LIST)
    Xtr = mlb.fit_transform(X_train)
    Xva = mlb.transform(X_val)
    Xte = mlb.transform(X_test)

    le = LabelEncoder()
    # fit on all labels seen in train
    ytr = le.fit_transform(y_train)

    clf = RandomForestClassifier(
        n_estimators=150,
        max_depth=16,
        min_samples_leaf=1,
        class_weight="balanced_subsample",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(Xtr, ytr)

    def eval_split(name, X, y_true_labels):
        # filter labels known to encoder
        known = set(le.classes_)
        pairs = [(x, y) for x, y in zip(X, y_true_labels) if y in known]
        if not pairs:
            return {}
        Xs = np.array([p[0] for p in pairs])
        ys = le.transform([p[1] for p in pairs])
        pred = clf.predict(Xs)
        y_true_str = le.inverse_transform(ys)
        y_pred_str = le.inverse_transform(pred)
        metrics = {
            "n": len(ys),
            "accuracy": round(float(accuracy_score(ys, pred)), 4),
            "precision_macro": round(float(precision_score(ys, pred, average="macro", zero_division=0)), 4),
            "recall_macro": round(float(recall_score(ys, pred, average="macro", zero_division=0)), 4),
            "f1_macro": round(float(f1_score(ys, pred, average="macro", zero_division=0)), 4),
            "f1_weighted": round(float(f1_score(ys, pred, average="weighted", zero_division=0)), 4),
        }
        report = classification_report(y_true_str, y_pred_str, zero_division=0, output_dict=True)
        cm = confusion_matrix(ys, pred)
        return {"metrics": metrics, "classification_report": report, "confusion_matrix_shape": list(cm.shape)}

    results = {
        "model": "RandomForest hybrid-rf-v3",
        "disclaimer": "Educational synthetic data only. Metrics are NOT clinical performance.",
        "train_size": len(y_train),
        "val": eval_split("val", Xva, y_val),
        "test": eval_split("test", Xte, y_test),
        "feature_importance_top15": [],
    }

    # feature importance
    importances = clf.feature_importances_
    top_idx = np.argsort(importances)[::-1][:15]
    results["feature_importance_top15"] = [
        {"symptom": SYMPTOM_LIST[i], "importance": round(float(importances[i]), 4)}
        for i in top_idx if importances[i] > 0
    ]

    # save model artifacts
    joblib.dump(clf, MODEL_DIR / "disease_rf_v3.joblib")
    joblib.dump(mlb, MODEL_DIR / "mlb_v3.joblib")
    joblib.dump(le, MODEL_DIR / "label_encoder_v3.joblib")
    (MODEL_DIR / "metrics_v3.json").write_text(json.dumps(results, indent=2))

    print(json.dumps(results["test"]["metrics"], indent=2))
    print("Saved models + metrics_v3.json")
    return results


if __name__ == "__main__":
    main()
