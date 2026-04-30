import sys
import os
sys.path.append(os.path.dirname(__file__))

import time
import numpy as np
import optuna
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from config import (
    HPO_TRAIN_CSV, HPO_TEST_CSV, FULL_TRAIN_CSV, FULL_TEST_CSV, RANDOM_SEED, N_TRIALS,
    load_data, encode_with_target,
    save_params, load_params, save_model, save_feature_importance,
)


PARAMS_FILE = "rf_best_params.json"
MODEL_FILE = "rf_model.pkl"


def hpo():
    """Optuna를 활용하여 최적 하이퍼파라미터를 탐색합니다."""
    X_train_full, y_train_full = load_data(HPO_TRAIN_CSV)
    _, X_hpo, _, y_hpo = train_test_split(
        X_train_full, y_train_full, test_size=0.1, stratify=y_train_full, random_state=RANDOM_SEED
    )

    X_htr, X_hval, y_htr, y_hval = train_test_split(
        X_hpo, y_hpo, test_size=0.2, stratify=y_hpo, random_state=RANDOM_SEED
    )

    X_htr, X_hval, _ = encode_with_target(X_htr, X_hval, y_htr)

    def objective(trial):
        params = {
            "n_estimators": trial.suggest_int("n_estimators", 50, 300),
            "max_depth": trial.suggest_int("max_depth", 5, 20),
            "min_samples_split": trial.suggest_int("min_samples_split", 2, 20),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 10),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", 0.5]),
            "random_state": RANDOM_SEED,
            "n_jobs": -1,
        }
        model = RandomForestClassifier(**params)
        model.fit(X_htr, y_htr)

        y_pred = model.predict(X_hval)
        return f1_score(y_hval, y_pred, average="macro")

    study = optuna.create_study(direction="maximize")
    study.optimize(objective, n_trials=N_TRIALS, show_progress_bar=True)

    best_params = study.best_params
    save_params(best_params, PARAMS_FILE)
    print(f"Best F1 Macro: {study.best_value:.4f}")


def train(mode: str = "mini"):
    """지정된 데이터 모드에 따라 모델을 학습하고 결과를 저장합니다."""
    if mode == "full":
        train_csv, test_csv = FULL_TRAIN_CSV, FULL_TEST_CSV
        print("전체 데이터 학습 시작")
    else:
        train_csv, test_csv = HPO_TRAIN_CSV, HPO_TEST_CSV
        print("미니배치 샘플 데이터 학습 시작")

    X_train, y_train = load_data(train_csv)
    X_test, _ = load_data(test_csv)
    X_train, X_test, encoders = encode_with_target(X_train, X_test, y_train)

    feature_names = X_train.columns.tolist()

    params = load_params(PARAMS_FILE)
    params.update({
        "random_state": RANDOM_SEED,
        "n_jobs": -1,
        "verbose": 1,
    })

    model = RandomForestClassifier(**params)

    start = time.time()
    model.fit(X_train, y_train)
    elapsed = time.time() - start

    save_model(model, encoders, MODEL_FILE)
    save_feature_importance(model.feature_importances_, feature_names, "rf")
    print(f"학습 완료 ({elapsed:.1f}초 소요)")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("hpo", "train_mini", "train_full"):
        print("Usage: python train_rf.py [hpo|train_mini|train_full]")
        sys.exit(1)

    if sys.argv[1] == "hpo":
        hpo()
    elif sys.argv[1] == "train_mini":
        train(mode="mini")
    elif sys.argv[1] == "train_full":
        train(mode="full")
