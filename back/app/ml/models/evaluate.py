import sys
import os
sys.path.append(os.path.dirname(__file__))

import glob
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    classification_report, confusion_matrix,
    roc_auc_score, average_precision_score,
    f1_score, precision_score, recall_score,
)
from config import (
    HPO_TEST_CSV, MODELS_DIR, PLOTS_DIR, CAT_COLS, STACK_MODEL_FILE,
    load_data, load_model, ensure_dirs,
)

REPORT_PATH = os.path.join(os.path.dirname(MODELS_DIR), "evaluation_report.txt")


def predict_proba_with_artifact(artifact, X_test: pd.DataFrame) -> np.ndarray:
    """저장된 모델 번들로 지연 확률(class=1)을 반환합니다."""
    model    = artifact["model"]
    encoders = artifact["encoders"]

    if isinstance(encoders, dict):
        # XGBoost / LightGBM: category dtype 인코딩
        for col, cats in encoders.items():
            if col in X_test.columns:
                cat_type = pd.CategoricalDtype(categories=cats)
                X_test[col] = X_test[col].astype(str).astype(cat_type)
    else:
        # RandomForest: TargetEncoder 변환
        cols = [c for c in CAT_COLS if c in X_test.columns]
        for col in cols:
            X_test[col] = X_test[col].astype(str)
        X_test[cols] = encoders.transform(X_test[cols])

    return model.predict_proba(X_test)[:, 1]


def save_confusion_matrix_plot(cm, model_name: str):
    ensure_dirs()
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["정시(0)", "지연(1)"],
        yticklabels=["정시(0)", "지연(1)"],
        ax=ax,
    )
    ax.set_xlabel("Predicted")
    ax.set_ylabel("Actual")
    ax.set_title(f"{model_name} - Confusion Matrix")
    plt.tight_layout()
    path = os.path.join(PLOTS_DIR, f"{model_name.lower()}_confusion_matrix.png")
    fig.savefig(path, dpi=150)
    plt.close(fig)
    print(f"Confusion Matrix 저장: {path}")


def evaluate_single(artifact, X_test: pd.DataFrame, y_test, model_name: str) -> tuple[float, str]:
    proba = predict_proba_with_artifact(artifact, X_test.copy())
    preds = (proba >= 0.5).astype(int)

    auc    = roc_auc_score(y_test, proba)
    ap     = average_precision_score(y_test, proba)
    report = classification_report(y_test, preds, target_names=["정시(0)", "지연(1)"])
    cm     = confusion_matrix(y_test, preds)

    print(f"\n[{model_name}]  AUC-ROC: {auc:.4f}  AP: {ap:.4f}")
    print(report)
    save_confusion_matrix_plot(cm, model_name)

    text_block = (
        f"[{model_name}]  AUC-ROC: {auc:.4f}   Average Precision: {ap:.4f}\n"
        f"{report}\n"
        f"Confusion Matrix:\n{cm}\n\n"
    )
    return auc, text_block


def evaluate_stacking(X_test: pd.DataFrame, y_test, test_csv: str) -> tuple[float, str] | None:
    """stack_model.pkl이 있으면 스태킹 모델도 평가합니다."""
    stack_path = os.path.join(MODELS_DIR, STACK_MODEL_FILE)
    if not os.path.exists(stack_path):
        return None

    import joblib
    artifact = joblib.load(stack_path)
    xgb, lgbm, rf, meta = artifact["xgb"], artifact["lgbm"], artifact["rf"], artifact["meta"]

    # XGBoost / LightGBM: category dtype 인코딩은 모델 내부에서 처리됨
    # RF: TargetEncoder는 stacking 학습 시와 다를 수 있으므로 저장된 te 사용
    te = artifact.get("te_rf")

    def _cat_encode(X):
        X = X.copy()
        for col in CAT_COLS:
            if col in X.columns:
                cats = artifact["cat_vocab"].get(col, sorted(X[col].astype(str).unique()))
                X[col] = X[col].astype(str).astype(pd.CategoricalDtype(categories=cats))
        return X

    def _te_encode(X):
        X = X.copy()
        if te is not None:
            cols = [c for c in CAT_COLS if c in X.columns]
            for col in cols:
                X[col] = X[col].astype(str)
            X[cols] = te.transform(X[cols])
        return X

    X_cat = _cat_encode(X_test)
    X_te  = _te_encode(X_test)

    p_xgb  = xgb.predict_proba(X_cat)[:, 1]
    p_lgbm = lgbm.predict_proba(X_cat)[:, 1]
    p_rf   = rf.predict_proba(X_te)[:, 1]

    meta_feat  = np.column_stack([p_xgb, p_lgbm, p_rf])
    p_stack    = meta.predict_proba(meta_feat)[:, 1]
    preds      = (p_stack >= 0.5).astype(int)

    auc    = roc_auc_score(y_test, p_stack)
    ap     = average_precision_score(y_test, p_stack)
    report = classification_report(y_test, preds, target_names=["정시(0)", "지연(1)"])
    cm     = confusion_matrix(y_test, preds)

    print(f"\n[STACKING]  AUC-ROC: {auc:.4f}  AP: {ap:.4f}")
    print(report)
    save_confusion_matrix_plot(cm, "stacking")

    text_block = (
        f"[STACKING]  AUC-ROC: {auc:.4f}   Average Precision: {ap:.4f}\n"
        f"{report}\n"
        f"Confusion Matrix:\n{cm}\n\n"
    )
    return auc, text_block


def compare_all(test_csv: str = None):
    from config import HPO_TEST_CSV
    csv_path = test_csv or HPO_TEST_CSV
    X_test_raw, y_test = load_data(csv_path)

    model_files = [
        f for f in glob.glob(os.path.join(MODELS_DIR, "*.pkl"))
        if os.path.basename(f) != STACK_MODEL_FILE
    ]
    if not model_files:
        print(f"저장된 모델이 없습니다: {MODELS_DIR}")
        return

    results      = {}
    report_texts = []

    for path in sorted(model_files):
        name     = os.path.basename(path).replace("_model.pkl", "").upper()
        artifact = load_model(os.path.basename(path))
        auc, text_block = evaluate_single(artifact, X_test_raw.copy(), y_test, name)
        results[name] = auc
        report_texts.append(text_block)

    # 스태킹 평가 (파일이 있을 때만)
    stack_result = evaluate_stacking(X_test_raw.copy(), y_test, csv_path)
    if stack_result:
        auc, text_block = stack_result
        results["STACKING"] = auc
        report_texts.append(text_block)

    ranking_text = "\n[AUC-ROC Ranking]\n"
    for name, score in sorted(results.items(), key=lambda x: x[1], reverse=True):
        ranking_text += f"  {name:20s} : {score:.4f}\n"

    print(ranking_text)

    ensure_dirs()
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("Flight Delay Binary Prediction -- Model Evaluation Report\n")
        f.write(f"Test Data: {csv_path}\n\n")
        for block in report_texts:
            f.write(block)
        f.write(ranking_text)

    print(f"평가 리포트 저장: {REPORT_PATH}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="전체 테스트 데이터 사용")
    args = parser.parse_args()
    from config import FULL_TEST_CSV
    compare_all(test_csv=FULL_TEST_CSV if args.full else None)
