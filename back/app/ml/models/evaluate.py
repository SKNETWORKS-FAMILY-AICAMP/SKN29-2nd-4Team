import sys
import os
sys.path.append(os.path.dirname(__file__))

import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from config import (
    HPO_TEST_CSV, FULL_TEST_CSV, MODELS_DIR, PLOTS_DIR, CAT_COLS, TARGET_COL,
    load_data, load_model, ensure_dirs,
)

LABELS = ["0: 정시", "1: 15분이하", "2: 15~180분", "3: 180분이상"]
REPORT_PATH = os.path.join(os.path.dirname(MODELS_DIR), "evaluation_report.txt")


def predict_with_artifact(artifact, X_test):
    """저장된 모델 번들로 새 데이터를 예측합니다."""
    model = artifact["model"]
    encoders = artifact["encoders"]
    model_type = type(model).__name__

    if model_type == "RandomForestClassifier":
        for col in CAT_COLS:
            if col in X_test.columns:
                X_test[col] = X_test[col].astype(str)
        cols = [c for c in CAT_COLS if c in X_test.columns]
        X_test[cols] = encoders.transform(X_test[cols])
    else:
        for col, cats in encoders.items():
            if col in X_test.columns:
                cat_type = pd.CategoricalDtype(categories=cats)
                X_test[col] = X_test[col].astype(str).astype(cat_type)

    return model.predict(X_test)


def save_confusion_matrix_plot(cm, model_name: str):
    """Confusion Matrix를 히트맵으로 시각화하여 PNG로 저장합니다."""
    ensure_dirs()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=LABELS, yticklabels=LABELS, ax=ax
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"{model_name} - Confusion Matrix")
    plt.tight_layout()

    path = os.path.join(PLOTS_DIR, f"{model_name.lower()}_confusion_matrix.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Confusion Matrix 저장: {path}")


def evaluate_model(artifact, X_test, y_test, model_name: str) -> tuple[float, str, np.ndarray]:
    """단일 모델의 성능을 평가하고 결과를 반환합니다."""
    y_pred = predict_with_artifact(artifact, X_test.copy())

    report = classification_report(y_test, y_pred, target_names=LABELS)
    cm = confusion_matrix(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="macro")

    # 터미널 출력
    print(f"\n[{model_name}]")
    print(report)
    print(cm)

    # Confusion Matrix PNG 저장
    save_confusion_matrix_plot(cm, model_name)

    # 텍스트 리포트 반환
    text_block = (
        f"[{model_name}]  F1 Macro: {f1:.4f}\n"
        f"{report}\n"
        f"Confusion Matrix:\n{cm}\n\n"
    )

    return f1, text_block, cm


def compare_all(test_csv: str = None):
    """저장된 모든 모델의 성능을 일괄 비교합니다."""
    csv_path = test_csv or HPO_TEST_CSV
    _, y_test = load_data(csv_path)
    df_test = pd.read_csv(csv_path)
    X_test_raw = df_test.drop(columns=[TARGET_COL])

    model_files = glob.glob(os.path.join(MODELS_DIR, "*.pkl"))

    if not model_files:
        print(f"저장된 모델이 없습니다: {MODELS_DIR}")
        return

    results = {}
    report_texts = []

    for path in sorted(model_files):
        name = os.path.basename(path).replace("_model.pkl", "").upper()
        artifact = load_model(os.path.basename(path))
        f1, text_block, _ = evaluate_model(artifact, X_test_raw.copy(), y_test, name)
        results[name] = f1
        report_texts.append(text_block)

    # 순위표 생성
    ranking_text = "\n[F1 Macro Ranking]\n"
    for name, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        ranking_text += f"  {name:20s} : {score:.4f}\n"

    print(ranking_text)

    # 전체 리포트를 텍스트 파일로 저장
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("Flight Delay Prediction - Model Evaluation Report\n")
        f.write(f"Test Data: {csv_path}\n\n")
        for block in report_texts:
            f.write(block)
        f.write(ranking_text)

    print(f"평가 리포트 저장: {REPORT_PATH}")


if __name__ == "__main__":
    compare_all()
