import joblib
import numpy as np
import pandas as pd
import torch

BASE = "back/models"

print("💫 loading models from pkl")
lgbm_artifact = joblib.load(BASE + '/lgbm_model.pkl')
xgb_artifact = joblib.load(BASE + '/xgboost_model.pkl')
rf_artifact = joblib.load(BASE + '/rf_model.pkl')
meta_model = joblib.load(BASE + '/stacking_meta_rev_03.pkl')
# fcnn_artifact = joblib.load(BASE + '/FCNN_rev02.pkl')

def test():
    print("===== FCNN ARTIFACT DEBUG =====")

    print(f"type: {type(fcnn_artifact)}")

    if isinstance(fcnn_artifact, dict):
        for k, v in fcnn_artifact.items():
            print(f"\n[key] {k}")
            print(f"  type: {type(v)}")

            # model이면 추가 정보
            if hasattr(v, "__class__"):
                print(f"  class: {v.__class__.__name__}")

            # sklearn / torch 공통적으로 자주 보는 속성
            if hasattr(v, "shape"):
                print(f"  shape: {v.shape}")

            if hasattr(v, "feature_names_in_"):
                print(f"  feature_names_in_: {list(v.feature_names_in_)[:5]} ...")

    else:
        print("artifact is not dict")
        print(f"repr: {repr(fcnn_artifact)}")

    print(fcnn_artifact['model'].keys())
    print(fcnn_artifact['label_encoders'].keys())
    print("================================")
# test()

def predict(input_df: pd.DataFrame):
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

# def fcnn_predict(input_df):
#     fcnn_artifact['model'] # <class 'dict'> ['epoch', 'model_state', 'vocab_sizes', 'n_static_num', 'n_dynamic', 'best_auc']
#     fcnn_artifact['scaler'] # <class 'sklearn.preprocessing._data.StandardScaler'>
#     fcnn_artifact['label_encoders'] # <class 'dict'> ['Marketing_Airline_Network', 'Operating_Airline', 'Origin', 'Dest']

#     model_info = fcnn_artifact['model']

#     model = FCNN(
#         vocab_sizes=model_info['vocab_sizes'],
#         n_static_num=model_info['n_static_num'],
#         n_dynamic=model_info['n_dynamic']
#     )

#     model.load_state_dict(model_info['model_state'])
#     model.eval()

#     X = preprocess_fcnn(input_df.copy())
#     X_tensor = torch.tensor(X, dtype=torch.float32)

#     with torch.no_grad():
#         logits = model(X_tensor)
#         probs = torch.sigmoid(logits).squeeze().cpu().numpy().tolist()

#     return probs


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

def preprocess_fcnn(X: pd.DataFrame):
    # 1️⃣ label encoding
    label_encoders = fcnn_artifact['label_encoders']
    for col, enc in label_encoders.items():
        X[col] = enc.transform(X[col])

    # 2️⃣ scaling
    scaler = fcnn_artifact['scaler']
    X_scaled = scaler.transform(X)

    return X_scaled