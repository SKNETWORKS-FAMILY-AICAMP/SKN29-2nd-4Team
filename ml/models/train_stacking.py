"""
Blending Stacking Pipeline  (pre-trained base models)
  base layer  -- XGBoost + LightGBM + RandomForest
                 (loaded from back/data/outputs/saved_models/)
  meta layer  -- LogisticRegression
                 (trained on 30% blend-set predictions)
  evaluation  -- ROC-AUC | Avg Precision | Accuracy | 지연 P/R/F1
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import numpy as np
import pandas as pd
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    roc_auc_score, average_precision_score, accuracy_score,
    precision_recall_fscore_support,
)
from ml.models.config import (
    FULL_TRAIN_CSV, FULL_TEST_CSV,
    RANDOM_SEED, CAT_COLS, MODELS_DIR,
    STACK_MODEL_FILE, load_data, ensure_dirs,
)


# ── 인코딩 헬퍼 ──────────────────────────────────────────────────────────────

def _ensure_route(X: pd.DataFrame) -> pd.DataFrame:
    """Route 컬럼이 없으면 Origin-Dest 조합으로 복원."""
    if "Route" not in X.columns and "Origin" in X.columns and "Dest" in X.columns:
        X["Route"] = X["Origin"].astype(str) + "-" + X["Dest"].astype(str)
    return X


def _apply_cat_vocab(X: pd.DataFrame, vocab: dict, feature_order: list) -> pd.DataFrame:
    """XGBoost / LightGBM 용: 저장된 vocab으로 category dtype 적용.
    미지 범주는 NaN 처리 (Pandas 4 호환). 컬럼 순서를 학습 당시와 동일하게 맞춤."""
    X = _ensure_route(X.copy())
    for col, cats in vocab.items():
        if col in X.columns:
            X[col] = pd.Categorical(X[col].astype(str), categories=cats)
    return X[feature_order]


def _apply_target_enc(X: pd.DataFrame, te, feature_order: list) -> pd.DataFrame:
    """RandomForest 용: 저장된 TargetEncoder 적용. 컬럼 순서를 학습 당시와 동일하게 맞춤."""
    X = _ensure_route(X.copy())
    fit_cols = list(te.feature_names_in_)
    for col in fit_cols:
        if col in X.columns:
            X[col] = X[col].astype(str)
    X[fit_cols] = te.transform(X[fit_cols])
    return X[feature_order]


# ── 메트릭 계산 ──────────────────────────────────────────────────────────────

def _metrics(y_true, p_prob, label: str) -> dict:
    preds = (p_prob >= 0.5).astype(int)
    prec, rec, f1, _ = precision_recall_fscore_support(
        y_true, preds, labels=[1], zero_division=0
    )
    return {
        "모델":           label,
        "ROC-AUC":        roc_auc_score(y_true, p_prob),
        "Avg Precision":  average_precision_score(y_true, p_prob),
        "Accuracy":       accuracy_score(y_true, preds),
        "지연 Precision": prec[0],
        "지연 Recall":    rec[0],
        "지연 F1":        f1[0],
    }


# ── 메인 ─────────────────────────────────────────────────────────────────────

def train_stacking():
    ensure_dirs()

    print("=" * 65)
    print("Blending Stacking  --  pre-trained base models")
    print("=" * 65)

    # ── 데이터 로드 ───────────────────────────────────────────────────────────
    print("\n데이터 로드 ...")
    X_train_full, y_train_full = load_data(FULL_TRAIN_CSV)
    X_test,       y_test       = load_data(FULL_TEST_CSV)

    # 70 % base_train (Base 모델 학습용)  /  30 % blend_set (Meta 모델 학습용)
    X_base, X_blend, y_base, y_blend = train_test_split(
        X_train_full, y_train_full, test_size=0.30, stratify=y_train_full, random_state=RANDOM_SEED
    )
    print(f"  base_train={len(X_base):,}  blend_set={len(X_blend):,}  test={len(X_test):,}")

    # ── Base 모델 초기화 (파라미터 로드) ──────────────────────────────────────
    from xgboost import XGBClassifier
    from lightgbm import LGBMClassifier
    from sklearn.ensemble import RandomForestClassifier
    from ml.models.config import load_params, params_exist, compute_class_weights

    print("\nBase 모델 초기화 및 학습")

    # 1. XGBoost
    if params_exist("xgboost_best_params.json"):
        xgb_params = load_params("xgboost_best_params.json")
    else:
        xgb_params = {"n_estimators": 500, "max_depth": 6, "learning_rate": 0.05}
    xgb_params.update({"random_state": RANDOM_SEED, "n_jobs": -1, "enable_categorical": True})
    xgb = XGBClassifier(**xgb_params)

    # 2. LightGBM
    if params_exist("lgbm_best_params.json"):
        lgbm_params = load_params("lgbm_best_params.json")
    else:
        lgbm_params = {"n_estimators": 500, "num_leaves": 31, "learning_rate": 0.05}
    lgbm_params.update({"random_state": RANDOM_SEED, "n_jobs": -1})
    lgbm = LGBMClassifier(**lgbm_params)

    # 3. RandomForest
    if params_exist("rf_best_params.json"):
        rf_params = load_params("rf_best_params.json")
    else:
        rf_params = {"n_estimators": 200, "max_depth": 12}
    rf_params.update({"random_state": RANDOM_SEED, "n_jobs": -1})
    rf = RandomForestClassifier(**rf_params)

    # 1. XGB & LGBM (Category 인코딩)
    from ml.models.config import encode_as_category, encode_with_target
    
    # Route 컬럼 확보 후 피처 순서 결정
    X_base  = _ensure_route(X_base)
    X_blend = _ensure_route(X_blend)
    X_test  = _ensure_route(X_test)
    
    xgb_feat_order = X_base.columns.tolist()
    
    # X_base와 X_blend, X_test를 모두 고려하여 vocab 생성
    _, _, xgb_vocab = encode_as_category(X_base.copy(), pd.concat([X_blend, X_test]))
    
    Xb_cat  = _apply_cat_vocab(X_base,  xgb_vocab, xgb_feat_order)
    Xbl_cat = _apply_cat_vocab(X_blend, xgb_vocab, xgb_feat_order)
    Xt_cat  = _apply_cat_vocab(X_test,  xgb_vocab, xgb_feat_order)

    # XGB 학습 (class weight 적용)
    cw = compute_class_weights(y_base)
    sw = np.array([cw[c] for c in y_base])
    xgb.fit(Xb_cat, y_base, sample_weight=sw)
    print("  XGBoost 학습 완료")

    # LGBM 학습
    lgbm_feat_order = xgb_feat_order
    Xb_lgbm  = _apply_cat_vocab(X_base,  xgb_vocab, lgbm_feat_order)
    Xbl_lgbm = _apply_cat_vocab(X_blend, xgb_vocab, lgbm_feat_order)
    Xt_lgbm  = _apply_cat_vocab(X_test,  xgb_vocab, lgbm_feat_order)
    lgbm.fit(Xb_lgbm, y_base)
    print("  LightGBM 학습 완료")

    # 2. RandomForest (Target 인코딩)
    Xb_te, X_temp, te_rf = encode_with_target(X_base.copy(), pd.concat([X_blend, X_test]), y_base)
    rf_feat_order = X_base.columns.tolist()
    
    # encode_with_target이 반환한 X_temp에서 분리
    Xbl_te = X_temp.iloc[:len(X_blend)]
    Xt_te  = X_temp.iloc[len(X_blend):]
    
    rf.fit(Xb_te, y_base)
    print("  RandomForest 학습 완료")

    # ── base 예측 ─────────────────────────────────────────────────────────────
    print("\nbase 모델 예측 ...")
    p_xgb_bl  = xgb.predict_proba(Xbl_cat)[:, 1]
    p_xgb_te  = xgb.predict_proba(Xt_cat)[:, 1]

    p_lgbm_bl = lgbm.predict_proba(Xbl_lgbm)[:, 1]
    p_lgbm_te = lgbm.predict_proba(Xt_lgbm)[:, 1]

    p_rf_bl   = rf.predict_proba(Xbl_te)[:, 1]
    p_rf_te   = rf.predict_proba(Xt_te)[:, 1]

    # ── Meta-learner (LogisticRegression) ─────────────────────────────────────
    print("[Meta] LogisticRegression 학습 ...")
    meta_bl = np.column_stack([p_xgb_bl, p_lgbm_bl, p_rf_bl])
    meta_te = np.column_stack([p_xgb_te, p_lgbm_te, p_rf_te])

    meta = LogisticRegression(C=1.0, max_iter=1000, random_state=RANDOM_SEED)
    meta.fit(meta_bl, y_blend)

    coef = dict(zip(["xgb", "lgbm", "rf"], meta.coef_[0]))
    print(f"  meta coef: xgb={coef['xgb']:.3f}  lgbm={coef['lgbm']:.3f}  rf={coef['rf']:.3f}")

    p_stack = meta.predict_proba(meta_te)[:, 1]

    # ── 결과 집계 ─────────────────────────────────────────────────────────────
    rows = [
        _metrics(y_test, p_xgb_te,  "XGBoost"),
        _metrics(y_test, p_lgbm_te, "LightGBM"),
        _metrics(y_test, p_rf_te,   "RandomForest"),
        _metrics(y_test, p_stack,   "Stacking"),
    ]
    result = pd.DataFrame(rows).set_index("모델")

    print("\n" + "=" * 65)
    print("Test Set 평가 결과")
    print("=" * 65)
    print(result.to_string(float_format=lambda x: f"{x:.4f}"))
    print("=" * 65)

    artifact = {
        "meta": meta,
        "meta_coef": coef,
    }
    out_path = os.path.join(MODELS_DIR, STACK_MODEL_FILE)
    joblib.dump(artifact, out_path)
    print(f"\n스태킹 모델 저장 완료: {out_path} (용량 최적화)")


if __name__ == "__main__":
    train_stacking()
