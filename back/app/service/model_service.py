import joblib
import numpy as np
import pandas as pd

BASE = "back/models"

print("💫 loading models from pkl")
lgbm_artifact = joblib.load(BASE + '/lgbm_model.pkl')
xgb_artifact = joblib.load(BASE + '/xgboost_model.pkl')
rf_artifact = joblib.load(BASE + '/rf_model.pkl')
meta_model = joblib.load(BASE + '/stacking_meta_rev_03.pkl')


def stacking_predict(input_df: pd.DataFrame):
    X_lgbm = _encode_and_select(input_df.copy(), lgbm_artifact)
    X_rf   = _encode_and_select(input_df.copy(), rf_artifact)
    X_xgb  = _to_category_and_select(input_df.copy(), xgb_artifact)

    # ── Base 예측 ──
    prob_lgbm = lgbm_artifact['model'].predict_proba(X_lgbm)[:, 1]
    prob_xgb  = xgb_artifact['model'].predict_proba(X_xgb)[:, 1]
    prob_rf   = rf_artifact['model'].predict_proba(X_rf)[:, 1]

    # ── Stacking ──
    meta_input = np.column_stack([prob_lgbm, prob_xgb, prob_rf])
    final_prob = meta_model.predict_proba(meta_input)[:, 1]

    return final_prob

def xgb_predict(input_df):
    X_xgb = _to_category_and_select(input_df.copy(), xgb_artifact)
    prob_xgb = xgb_artifact['model'].predict_proba(X_xgb)[:, 1]
    return prob_xgb


def _encode_and_select(X: pd.DataFrame, artifact):
    model = artifact["model"]
    encoder = artifact.get("encoders", None)

    if encoder is None:
        raise RuntimeError("encoders 없음")

    # 인코딩 대상 컬럼
    if hasattr(encoder, "feature_names_in_"):
        enc_cols = list(encoder.feature_names_in_)
    else:
        raise RuntimeError("encoder feature_names_in_ 없음")

    missing = set(enc_cols) - set(X.columns)
    if missing:
        raise RuntimeError(f"encoder 기준 missing 컬럼: {missing}")

    # 일부만 인코딩
    X_enc_input = X[enc_cols]
    X_transformed = encoder.transform(X_enc_input)

    # ndarray → DataFrame
    if isinstance(X_transformed, np.ndarray):
        X_transformed = pd.DataFrame(
            X_transformed,
            columns=enc_cols,
            index=X.index
        )

    # 원본 X에 덮어쓰기
    X[enc_cols] = X_transformed

    # model 기준 align
    model_cols = list(model.feature_names_in_)
    missing = set(model_cols) - set(X.columns)
    if missing:
        raise RuntimeError(f"model 기준 missing 컬럼: {missing}")

    X = X[model_cols]

    return X

def _to_category_and_select(X: pd.DataFrame, artifact):
    model = artifact["model"]
    encoders = artifact.get("encoders", None)

    if encoders is None:
        raise RuntimeError("xgb encoders 없음")

    # encoders는 "categorical 컬럼 목록" 역할
    if isinstance(encoders, dict):
        cat_cols = list(encoders.keys())
    elif isinstance(encoders, (list, tuple)):
        cat_cols = list(encoders)
    else:
        raise RuntimeError(f"알 수 없는 encoders 타입: {type(encoders)}")

    # category dtype 적용
    for col in cat_cols:
        if col not in X.columns:
            raise RuntimeError(f"xgb categorical 컬럼 없음: {col}")
        X[col] = X[col].astype("category")

    # model 기준 align
    model_cols = list(model.feature_names_in_)
    missing = set(model_cols) - set(X.columns)
    if missing:
        raise RuntimeError(f"xgb model 기준 missing 컬럼: {missing}")

    X = X[model_cols]

    return X