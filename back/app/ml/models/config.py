import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import TargetEncoder

DATA_DIR   = r"C:\proj2\back\data"
REV03_DIR  = os.path.join(DATA_DIR, "processed", "rev_03")
PARAMS_DIR = os.path.join(DATA_DIR, "outputs", "params")
PLOTS_DIR  = os.path.join(DATA_DIR, "outputs", "plots")
MODELS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "saved_models")

HPO_TRAIN_CSV  = os.path.join(REV03_DIR, "flight_delay_train_clean.csv")
HPO_TEST_CSV   = os.path.join(REV03_DIR, "flight_delay_test_clean.csv")
FULL_TRAIN_CSV = os.path.join(REV03_DIR, "flight_delay_train_clean.csv")
FULL_TEST_CSV  = os.path.join(REV03_DIR, "flight_delay_test_clean.csv")

TARGET_COL  = "DelayCategory"
BINARY_MODE = True   # True: 0=정시, 1=지연(DelayCategory > 0)
RANDOM_SEED = 42
N_TRIALS    = 70

CAT_COLS = ["Marketing_Airline_Network", "Operating_Airline", "Origin", "Dest", "Route"]

STACK_MODEL_FILE = "stack_model.pkl"


def ensure_dirs():
    for d in [PARAMS_DIR, MODELS_DIR, PLOTS_DIR]:
        os.makedirs(d, exist_ok=True)


def load_data(csv_path: str) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(csv_path)
    if BINARY_MODE:
        y = (df[TARGET_COL] > 0).astype(int)
    else:
        y = df[TARGET_COL]
    X = df.drop(columns=[TARGET_COL])
    return X, y


def encode_as_category(X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """XGBoost/LightGBM용: pandas category dtype 변환."""
    cat_mappings = {}
    for col in CAT_COLS:
        if col in X_train.columns:
            all_cats = sorted(
                pd.concat([X_train[col], X_test[col]]).astype(str).unique()
            )
            cat_type = pd.CategoricalDtype(categories=all_cats)
            X_train[col] = X_train[col].astype(str).astype(cat_type)
            X_test[col]  = X_test[col].astype(str).astype(cat_type)
            cat_mappings[col] = all_cats
    return X_train, X_test, cat_mappings


def encode_with_target(X_train: pd.DataFrame, X_test: pd.DataFrame, y_train: pd.Series) -> tuple[pd.DataFrame, pd.DataFrame, TargetEncoder]:
    """RandomForest용: TargetEncoder 변환. X_train에 대해서만 fit."""
    for col in CAT_COLS:
        if col in X_train.columns:
            X_train[col] = X_train[col].astype(str)
            X_test[col]  = X_test[col].astype(str)

    cols_to_encode = [c for c in CAT_COLS if c in X_train.columns]
    target_type = "binary" if BINARY_MODE else "continuous"
    te = TargetEncoder(smooth="auto", target_type=target_type, random_state=RANDOM_SEED)
    X_train[cols_to_encode] = te.fit_transform(X_train[cols_to_encode], y_train)
    X_test[cols_to_encode]  = te.transform(X_test[cols_to_encode])
    return X_train, X_test, te


def compute_class_weights(y: pd.Series) -> dict:
    classes   = np.unique(y)
    n_samples = len(y)
    n_classes = len(classes)
    weights   = {}
    for c in classes:
        raw = n_samples / (n_classes * np.sum(y == c))
        weights[c] = np.sqrt(raw)
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


def params_exist(filename: str) -> bool:
    return os.path.exists(os.path.join(PARAMS_DIR, filename))


def save_model(model, encoders, filename: str):
    ensure_dirs()
    path = os.path.join(MODELS_DIR, filename)
    joblib.dump({"model": model, "encoders": encoders}, path)
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
