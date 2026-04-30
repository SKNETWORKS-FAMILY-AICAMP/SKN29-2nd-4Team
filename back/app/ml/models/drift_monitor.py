import sys
import os
sys.path.append(os.path.dirname(__file__))

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, classification_report, confusion_matrix
from config import (
    TARGET_COL, CAT_COLS,
    load_model, save_model,
)

F1_THRESHOLD = 0.45

LABELS = ["0: 정시", "1: 15분이하", "2: 15~180분", "3: 180분이상"]


def _encode_new_data(X_new: pd.DataFrame, model, encoders) -> pd.DataFrame:
    """모델 유형에 따라 새 데이터를 적절한 인코딩으로 변환합니다."""
    model_type = type(model).__name__

    if model_type == "RandomForestClassifier":
        # RF: TargetEncoder로 변환
        for col in CAT_COLS:
            if col in X_new.columns:
                X_new[col] = X_new[col].astype(str)
        cols = [c for c in CAT_COLS if c in X_new.columns]
        X_new[cols] = encoders.transform(X_new[cols])
    else:
        # XGBoost/LightGBM: category dtype으로 변환
        for col, cats in encoders.items():
            if col in X_new.columns:
                # 학습 시 없던 카테고리는 첫 번째 카테고리로 대체
                X_new[col] = X_new[col].astype(str).apply(
                    lambda x, c=cats: x if x in c else c[0]
                )
                cat_type = pd.CategoricalDtype(categories=cats)
                X_new[col] = X_new[col].astype(cat_type)

    return X_new


def check_drift(model_filename: str, new_csv_path: str, threshold: float = F1_THRESHOLD) -> dict:
    """
    저장된 모델에 새 데이터를 넣어서 성능 저하(Drift)를 감지한다.

    Returns:
        {"f1": float, "drifted": bool, "report": str}
    """
    artifact = load_model(model_filename)
    model = artifact["model"]
    encoders = artifact["encoders"]

    df = pd.read_csv(new_csv_path)
    y_new = df[TARGET_COL]
    X_new = df.drop(columns=[TARGET_COL])

    X_new = _encode_new_data(X_new, model, encoders)
    y_pred = model.predict(X_new)

    f1 = f1_score(y_new, y_pred, average="macro")
    drifted = f1 < threshold

    report = classification_report(y_new, y_pred, target_names=LABELS)
    cm = confusion_matrix(y_new, y_pred)

    print(f"\n{'='*50}")
    print(f"  Drift 검사: {model_filename}")
    print(f"  새 데이터: {new_csv_path}")
    print(f"  데이터 건수: {len(df):,}")
    print(f"{'='*50}")
    print(report)
    print("Confusion Matrix:")
    print(cm)
    print(f"\n  F1 Macro: {f1:.4f}  |  Threshold: {threshold}")

    if drifted:
        print(f"  [경고] 데이터 드리프트 감지 (F1: {f1:.4f} < Threshold: {threshold})")
    else:
        print(f"  [정상] 성능 기준 만족. 모델 업데이트 불필요.")
    print(f"{'='*50}")

    return {"f1": f1, "drifted": drifted, "report": report}


def update_model(model_filename: str, new_csv_path: str, threshold: float = F1_THRESHOLD):
    """
    새 데이터로 기존 모델을 증분 학습(Incremental Learning)한다.
    업데이트 후 성능이 threshold 이상인지 검증한다.

    XGBoost/LightGBM: 기존 모델 위에 추가 학습 (warm start)
    RandomForest: warm_start로 트리 추가
    """
    artifact = load_model(model_filename)
    model = artifact["model"]
    encoders = artifact["encoders"]

    df = pd.read_csv(new_csv_path)
    y_new = df[TARGET_COL]
    X_new = df.drop(columns=[TARGET_COL])

    X_new = _encode_new_data(X_new, model, encoders)

    # 모델 유형에 따라 증분 학습 방식 결정
    model_type = type(model).__name__

    if model_type == "XGBClassifier":
        model.fit(X_new, y_new, xgb_model=model.get_booster(), verbose=False)
        print("XGBoost 증분 학습 완료")

    elif model_type == "LGBMClassifier":
        model.fit(X_new, y_new, init_model=model, verbose=-1)
        print("LightGBM 증분 학습 완료")

    elif model_type == "RandomForestClassifier":
        model.set_params(warm_start=True)
        prev_n = model.n_estimators
        model.set_params(n_estimators=prev_n + 50)
        model.fit(X_new, y_new)
        print(f"RandomForest 증분 학습 완료 (트리 {prev_n} -> {prev_n + 50})")

    else:
        print(f"지원하지 않는 모델: {model_type}")
        return

    # 업데이트 후 검증
    y_pred = model.predict(X_new)
    f1_after = f1_score(y_new, y_pred, average="macro")

    print(f"\n  업데이트 후 F1 Macro: {f1_after:.4f}")

    if f1_after >= threshold:
        save_model(model, encoders, model_filename)
        print(f"  [성공] 업데이트 완료. Threshold({threshold}) 이상 만족, 모델 저장됨.")
    else:
        print(f"  [실패] Threshold({threshold}) 미달. 기존 모델 유지 (전체 재학습 필요 권장).")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python drift_monitor.py check  <model.pkl> <new_data.csv>")
        print("  python drift_monitor.py update <model.pkl> <new_data.csv>")
        sys.exit(1)

    action = sys.argv[1]
    model_file = sys.argv[2]
    new_csv = sys.argv[3]

    if action == "check":
        check_drift(model_file, new_csv)
    elif action == "update":
        result = check_drift(model_file, new_csv)
        if result["drifted"]:
            print("\nDrift 감지 -> 증분 학습을 시작합니다...")
            update_model(model_file, new_csv)
        else:
            print("\n성능 정상 -> 업데이트 건너뜀.")
    else:
        print(f"알 수 없는 명령: {action}")
