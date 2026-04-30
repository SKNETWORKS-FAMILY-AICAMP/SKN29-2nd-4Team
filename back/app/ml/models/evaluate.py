import sys
import os
sys.path.append(os.path.dirname(__file__))

import glob
import numpy as np
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from config import (
    TEST_CSV, TRAIN_CSV, MODELS_DIR, CAT_COLS, TARGET_COL,
    load_data, load_model,
)

LABELS = ["0: 정시", "1: 15분이하", "2: 15~180분", "3: 180분이상"]


def predict_with_artifact(artifact, X_test):
    model = artifact["model"]
    scaler = artifact["scaler"]
    encoders = artifact["encoders"]

    for col, le in encoders.items():
        if col in X_test.columns:
            X_test[col] = le.transform(X_test[col].astype(str))

    X_scaled = scaler.transform(X_test)
    return model.predict(X_scaled)


def evaluate_model(artifact, X_test, y_test, model_name: str):
    y_pred = predict_with_artifact(artifact, X_test.copy())

    print(f"\n{'='*50}")
    print(f"  {model_name}")
    print(f"{'='*50}")
    print(classification_report(y_test, y_pred, target_names=LABELS))
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    return f1_score(y_test, y_pred, average="macro")


def compare_all():
    _, y_test = load_data(TEST_CSV)
    df_test = pd.read_csv(TEST_CSV)
    X_test_raw = df_test.drop(columns=[TARGET_COL])

    model_files = glob.glob(os.path.join(MODELS_DIR, "*.pkl"))

    if not model_files:
        print(f"저장된 모델이 없습니다: {MODELS_DIR}")
        return

    results = {}
    for path in sorted(model_files):
        name = os.path.basename(path).replace("_model.pkl", "").upper()
        artifact = load_model(os.path.basename(path))
        f1 = evaluate_model(artifact, X_test_raw.copy(), y_test, name)
        results[name] = f1

    print(f"\n{'='*50}")
    print("  모델 성능 비교 (F1 Macro)")
    print(f"{'='*50}")
    for name, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        print(f"  {name:20s} : {score:.4f}")
    print(f"{'='*50}")


if __name__ == "__main__":
    compare_all()
