import sys
import os
sys.path.append(os.path.dirname(__file__))

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, classification_report, confusion_matrix
from ml.models.config import (
    TARGET_COL, BINARY_MODE, CAT_COLS,
    load_model, save_model,
)

AUC_THRESHOLD = 0.80      # 이 값 미만이면 드리프트로 판정 → 재학습 트리거

LABELS = ["정시(0)", "지연(1)"]


def _load_binary_target(df: pd.DataFrame) -> pd.Series:
    if BINARY_MODE:
        return (df[TARGET_COL] > 0).astype(int)
    return df[TARGET_COL].astype(int)


def _encode_new_data(X_new: pd.DataFrame, model, encoders) -> pd.DataFrame:
    """모델 유형에 따라 새 데이터를 인코딩한다."""
    model_type = type(model).__name__

    if model_type == "RandomForestClassifier":
        for col in CAT_COLS:
            if col in X_new.columns:
                X_new[col] = X_new[col].astype(str)
        cols = [c for c in CAT_COLS if c in X_new.columns]
        X_new[cols] = encoders.transform(X_new[cols])
    else:
        # XGBoost / LightGBM: category dtype
        for col, cats in encoders.items():
            if col in X_new.columns:
                X_new[col] = X_new[col].astype(str).apply(
                    lambda x, c=cats: x if x in c else c[0]
                )
                X_new[col] = X_new[col].astype(pd.CategoricalDtype(categories=cats))

    return X_new


def check_drift(model_filename: str, new_csv_path: str, threshold: float = AUC_THRESHOLD) -> dict:
    """
    저장된 모델로 새 데이터를 평가하여 성능 저하(Drift)를 감지한다.

    Returns:
        {"auc": float, "drifted": bool, "report": str}
    """
    artifact = load_model(model_filename)
    model    = artifact["model"]
    encoders = artifact["encoders"]

    df    = pd.read_csv(new_csv_path)
    y_new = _load_binary_target(df)
    X_new = df.drop(columns=[TARGET_COL])

    X_new  = _encode_new_data(X_new, model, encoders)
    y_prob = model.predict_proba(X_new)[:, 1]
    y_pred = (y_prob >= 0.5).astype(int)

    auc     = roc_auc_score(y_new, y_prob)
    drifted = auc < threshold

    report = classification_report(y_new, y_pred, target_names=LABELS)
    cm     = confusion_matrix(y_new, y_pred)

    print(f"\n{'='*55}")
    print(f"  Drift 검사: {model_filename}")
    print(f"  새 데이터 : {new_csv_path}  ({len(df):,}건)")
    print(f"{'='*55}")
    print(report)
    print("Confusion Matrix:")
    print(cm)
    print(f"\n  ROC-AUC: {auc:.4f}  |  Threshold: {threshold}")

    if drifted:
        print(f"  [경고] 드리프트 감지 — ROC-AUC {auc:.4f} < {threshold}  →  재학습 필요")
    else:
        print(f"  [정상] 성능 기준 만족 (ROC-AUC {auc:.4f} ≥ {threshold})")
    print(f"{'='*55}")

    return {"auc": auc, "drifted": drifted, "report": report}


def update_model(model_filename: str, new_csv_path: str, threshold: float = AUC_THRESHOLD):
    """
    새 데이터로 기존 모델을 증분 학습(Incremental Learning)한다.
    업데이트 후 ROC-AUC가 threshold 이상인지 검증 후 저장한다.

    XGBoost    : xgb_model=model.get_booster() 로 이어 학습
    LightGBM   : init_model=model 로 이어 학습
    RandomForest: warm_start=True + 트리 50개 추가
    """
    artifact = load_model(model_filename)
    model    = artifact["model"]
    encoders = artifact["encoders"]

    df    = pd.read_csv(new_csv_path)
    y_new = _load_binary_target(df)
    X_new = df.drop(columns=[TARGET_COL])
    X_new = _encode_new_data(X_new, model, encoders)

    model_type = type(model).__name__

    if model_type == "XGBClassifier":
        model.fit(X_new, y_new, xgb_model=model.get_booster(), verbose=False)
        print("XGBoost 증분 학습 완료")

    elif model_type == "LGBMClassifier":
        model.fit(X_new, y_new, init_model=model, verbose=-1)
        print("LightGBM 증분 학습 완료")

    elif model_type == "RandomForestClassifier":
        prev_n = model.n_estimators
        model.set_params(warm_start=True, n_estimators=prev_n + 50)
        model.fit(X_new, y_new)
        print(f"RandomForest 증분 학습 완료 (트리 {prev_n} → {prev_n + 50})")

    else:
        print(f"지원하지 않는 모델 유형: {model_type}")
        return

    # 업데이트 후 검증
    y_prob_after = model.predict_proba(X_new)[:, 1]
    auc_after    = roc_auc_score(y_new, y_prob_after)

    print(f"\n  업데이트 후 ROC-AUC: {auc_after:.4f}")

    if auc_after >= threshold:
        save_model(model, encoders, model_filename)
        print(f"  [성공] 모델 저장 완료 — ROC-AUC {auc_after:.4f} ≥ {threshold}")
    else:
        print(f"  [실패] ROC-AUC {auc_after:.4f} < {threshold} — 기존 모델 유지 (전체 재학습 권장)")


if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage:")
        print("  python drift_monitor.py check  <model.pkl> <new_data.csv>")
        print("  python drift_monitor.py update <model.pkl> <new_data.csv>")
        sys.exit(1)

    action     = sys.argv[1]
    model_file = sys.argv[2]
    new_csv    = sys.argv[3]

    if action == "check":
        check_drift(model_file, new_csv)
    elif action == "update":
        result = check_drift(model_file, new_csv)
        if result["drifted"]:
            print("\n드리프트 감지 → 증분 학습을 시작합니다...")
            update_model(model_file, new_csv)
        else:
            print("\n성능 정상 → 업데이트 건너뜀.")
    else:
        print(f"알 수 없는 명령: {action}  (check / update 중 선택)")
