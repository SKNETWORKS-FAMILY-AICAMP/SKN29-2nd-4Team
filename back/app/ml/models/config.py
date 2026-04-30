import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, RobustScaler
from sklearn.model_selection import StratifiedKFold

# 경로
DATA_DIR = r"C:\proj2\back\data"
REV02_DIR = os.path.join(DATA_DIR, "processed", "rev_02")
MINIBATCH_DIR = os.path.join(DATA_DIR, "minibatch")
PARAMS_DIR = os.path.join(DATA_DIR, "outputs", "params")
MODELS_DIR = os.path.join(DATA_DIR, "outputs", "saved_models")
PLOTS_DIR = os.path.join(DATA_DIR, "outputs", "plots")

# HPO용 미니배치 (10% 샘플)
HPO_TRAIN_CSV = os.path.join(MINIBATCH_DIR, "minibatch_flight_delay_train_clean.csv")
HPO_TEST_CSV = os.path.join(MINIBATCH_DIR, "minibatch_flight_delay_test_clean.csv")

# 최종 학습 및 평가용 전체 데이터 (2600만 건)
FULL_TRAIN_CSV = os.path.join(REV02_DIR, "flight_delay_train_clean.csv")
FULL_TEST_CSV = os.path.join(REV02_DIR, "flight_delay_test_clean.csv")

TARGET_COL = "DelayCategory"
RANDOM_SEED = 42
N_SPLITS = 5
N_TRIALS = 100

# 범주형 컬럼
CAT_COLS = ["Marketing_Airline_Network", "Operating_Airline", "Origin", "Dest", "Route"]


def ensure_dirs():
    for d in [PARAMS_DIR, MODELS_DIR, PLOTS_DIR]:
        os.makedirs(d, exist_ok=True)


def load_data(csv_path: str) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(csv_path)
    y = df[TARGET_COL]
    X = df.drop(columns=[TARGET_COL])
    return X, y


def encode_categoricals(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    encoders = {}
    for col in CAT_COLS:
        if col in X_train.columns:
            le = LabelEncoder()
            le.fit(pd.concat([X_train[col], X_test[col]]).astype(str))
            X_train[col] = le.transform(X_train[col].astype(str))
            X_test[col] = le.transform(X_test[col].astype(str))
            encoders[col] = le
    return X_train, X_test, encoders


def scale_features(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, RobustScaler]:
    scaler = RobustScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    return X_train_scaled, X_test_scaled, scaler


def get_cv():
    return StratifiedKFold(n_splits=N_SPLITS, shuffle=True, random_state=RANDOM_SEED)


def compute_class_weights(y: pd.Series) -> dict:
    classes = np.unique(y)
    n_samples = len(y)
    n_classes = len(classes)
    weights = {}
    for c in classes:
        weights[c] = n_samples / (n_classes * np.sum(y == c))
    return weights


def save_params(params: dict, filename: str):
    ensure_dirs()
    path = os.path.join(PARAMS_DIR, filename)
    with open(path, "w") as f:
        json.dump(params, f, indent=2)
    print(f"파라미터 저장: {path}")


def load_params(filename: str) -> dict:
    path = os.path.join(PARAMS_DIR, filename)
    with open(path) as f:
        return json.load(f)


def save_model(model, scaler, encoders, filename: str):
    ensure_dirs()
    path = os.path.join(MODELS_DIR, filename)
    artifact = {"model": model, "scaler": scaler, "encoders": encoders}
    joblib.dump(artifact, path)
    print(f"모델 저장: {path}")


def load_model(filename: str):
    path = os.path.join(MODELS_DIR, filename)
    return joblib.load(path)


def save_feature_importance(importances, feature_names, model_name: str):
    ensure_dirs()
    fi = pd.DataFrame({"feature": feature_names, "importance": importances})
    fi = fi.sort_values("importance", ascending=False).head(20)

    plt.figure(figsize=(10, 8))
    plt.barh(fi["feature"][::-1], fi["importance"][::-1])
    plt.title(f"{model_name} - Top 20 Feature Importance")
    plt.xlabel("Importance")
    plt.tight_layout()

    path = os.path.join(PLOTS_DIR, f"{model_name}_feature_importance.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"피처 중요도 저장: {path}")
