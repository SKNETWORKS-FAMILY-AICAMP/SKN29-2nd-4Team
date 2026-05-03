"""
Blending Stacking Pipeline
  base layer  -- XGBoost + LightGBM + RandomForest
                 (trained on 70% of mini train)
  meta layer  -- LogisticRegression
                 (trained on 30% blending set, no data leakage)
  evaluation  -- AUC-ROC on test set
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

import json
import numpy as np
import pandas as pd
import joblib
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier, early_stopping, log_evaluation
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import TargetEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, average_precision_score, classification_report
from config import (
    HPO_TRAIN_CSV, HPO_TEST_CSV,
    FULL_TRAIN_CSV, FULL_TEST_CSV,
    RANDOM_SEED, CAT_COLS, BINARY_MODE, MODELS_DIR, PARAMS_DIR,
    STACK_MODEL_FILE, load_data, ensure_dirs,
)

# ── 기본 하이퍼파라미터 (HPO JSON 없을 때 fallback) ────────────────────────────
_XGB_DEFAULTS = {
    "n_estimators": 500, "max_depth": 6, "learning_rate": 0.05,
    "subsample": 0.8, "colsample_bytree": 0.8,
}
_LGBM_DEFAULTS = {
    "n_estimators": 500, "num_leaves": 63, "learning_rate": 0.05,
    "subsample": 0.8, "colsample_bytree": 0.8,
}
_RF_DEFAULTS = {
    "n_estimators": 200, "max_depth": 12, "min_samples_split": 5,
    "min_samples_leaf": 2, "max_features": "sqrt", "class_weight": "balanced",
}


def _load_hpo(filename: str, defaults: dict) -> dict:
    path = os.path.join(PARAMS_DIR, filename)
    if os.path.exists(path):
        with open(path) as f:
            hpo = json.load(f)
        print(f"  HPO 로드: {filename}")
        return {**defaults, **hpo}
    print(f"  HPO 없음 → 기본값 사용: {filename}")
    return defaults.copy()


def _encode_cat(X_base, X_blend, X_test):
    """XGBoost/LightGBM용 category dtype. 어휘는 세 데이터셋 합집합."""
    X_base, X_blend, X_test = X_base.copy(), X_blend.copy(), X_test.copy()
    vocab = {}
    for col in CAT_COLS:
        if col not in X_base.columns:
            continue
        all_cats = sorted(
            pd.concat([X_base[col], X_blend[col], X_test[col]]).astype(str).unique()
        )
        cat_type = pd.CategoricalDtype(categories=all_cats)
        X_base[col]  = X_base[col].astype(str).astype(cat_type)
        X_blend[col] = X_blend[col].astype(str).astype(cat_type)
        X_test[col]  = X_test[col].astype(str).astype(cat_type)
        vocab[col] = all_cats
    return X_base, X_blend, X_test, vocab


def _encode_target(X_base, X_blend, X_test, y_base):
    """RF용 TargetEncoder. y_base에 대해서만 fit (누수 방지)."""
    X_base, X_blend, X_test = X_base.copy(), X_blend.copy(), X_test.copy()
    cols = [c for c in CAT_COLS if c in X_base.columns]
    for df_ in [X_base, X_blend, X_test]:
        for col in cols:
            df_[col] = df_[col].astype(str)
    target_type = "binary" if BINARY_MODE else "continuous"
    te = TargetEncoder(smooth="auto", target_type=target_type, random_state=RANDOM_SEED)
    X_base[cols]  = te.fit_transform(X_base[cols], y_base)
    X_blend[cols] = te.transform(X_blend[cols])
    X_test[cols]  = te.transform(X_test[cols])
    return X_base, X_blend, X_test, te


def train_stacking(use_full: bool = False):
    ensure_dirs()

    train_csv = FULL_TRAIN_CSV if use_full else HPO_TRAIN_CSV
    test_csv  = FULL_TEST_CSV  if use_full else HPO_TEST_CSV
    mode_label = "전체 데이터" if use_full else "미니배치"

    print("=" * 60)
    print(f"Blending Stacking  --  {mode_label}")
    print("=" * 60)

    print("\n데이터 로드 ...")
    X_train, y_train = load_data(train_csv)
    X_test,  y_test  = load_data(test_csv)

    # 70% base_train / 30% blend_set
    X_base, X_blend, y_base, y_blend = train_test_split(
        X_train, y_train, test_size=0.30, stratify=y_train, random_state=RANDOM_SEED
    )
    print(f"  base_train={len(X_base):,}  blend_set={len(X_blend):,}  test={len(X_test):,}")

    # ── 인코딩 ─────────────────────────────────────────────────────────────────
    Xb_cat, Xbl_cat, Xt_cat, cat_vocab = _encode_cat(X_base, X_blend, X_test)
    Xb_te,  Xbl_te,  Xt_te,  te        = _encode_target(X_base, X_blend, X_test, y_base)

    # ── [1/3] XGBoost ──────────────────────────────────────────────────────────
    print("\n[1/3] XGBoost 학습 ...")
    xgb_p = _load_hpo("xgboost_best_params.json", _XGB_DEFAULTS)
    xgb_p.update({
        "objective": "binary:logistic", "eval_metric": "logloss",
        "tree_method": "hist", "enable_categorical": True,
        "early_stopping_rounds": 50, "random_state": RANDOM_SEED, "n_jobs": -1,
    })
    xgb = XGBClassifier(**xgb_p)
    xgb.fit(Xb_cat, y_base, eval_set=[(Xbl_cat, y_blend)], verbose=False)
    p_xgb_bl = xgb.predict_proba(Xbl_cat)[:, 1]
    p_xgb_te = xgb.predict_proba(Xt_cat)[:, 1]
    print(f"  AUC (blend)={roc_auc_score(y_blend, p_xgb_bl):.4f}  "
          f"AUC (test)={roc_auc_score(y_test, p_xgb_te):.4f}")

    # ── [2/3] LightGBM ─────────────────────────────────────────────────────────
    print("\n[2/3] LightGBM 학습 ...")
    lgbm_p = _load_hpo("lgbm_best_params.json", _LGBM_DEFAULTS)
    lgbm_p.update({
        "objective": "binary", "random_state": RANDOM_SEED, "n_jobs": -1, "verbose": -1,
    })
    lgbm = LGBMClassifier(**lgbm_p)
    lgbm.fit(
        Xb_cat, y_base,
        eval_set=[(Xbl_cat, y_blend)],
        callbacks=[early_stopping(50, verbose=False), log_evaluation(0)],
    )
    p_lgbm_bl = lgbm.predict_proba(Xbl_cat)[:, 1]
    p_lgbm_te = lgbm.predict_proba(Xt_cat)[:, 1]
    print(f"  AUC (blend)={roc_auc_score(y_blend, p_lgbm_bl):.4f}  "
          f"AUC (test)={roc_auc_score(y_test, p_lgbm_te):.4f}")

    # ── [3/3] RandomForest ─────────────────────────────────────────────────────
    print("\n[3/3] RandomForest 학습 ...")
    rf_p = _load_hpo("rf_best_params.json", _RF_DEFAULTS)
    rf_p.update({"random_state": RANDOM_SEED, "n_jobs": -1})
    rf = RandomForestClassifier(**rf_p)
    rf.fit(Xb_te, y_base)
    p_rf_bl = rf.predict_proba(Xbl_te)[:, 1]
    p_rf_te = rf.predict_proba(Xt_te)[:, 1]
    print(f"  AUC (blend)={roc_auc_score(y_blend, p_rf_bl):.4f}  "
          f"AUC (test)={roc_auc_score(y_test, p_rf_te):.4f}")

    # ── Meta-learner (LogisticRegression) ──────────────────────────────────────
    print("\n[Meta] LogisticRegression 학습 ...")
    meta_bl = np.column_stack([p_xgb_bl, p_lgbm_bl, p_rf_bl])
    meta_te = np.column_stack([p_xgb_te, p_lgbm_te, p_rf_te])

    meta = LogisticRegression(C=1.0, max_iter=1000, random_state=RANDOM_SEED)
    meta.fit(meta_bl, y_blend)

    coef = dict(zip(["xgb", "lgbm", "rf"], meta.coef_[0]))
    print(f"  meta coef: xgb={coef['xgb']:.3f}  lgbm={coef['lgbm']:.3f}  rf={coef['rf']:.3f}")

    # ── 최종 평가 ──────────────────────────────────────────────────────────────
    p_stack = meta.predict_proba(meta_te)[:, 1]
    preds   = (p_stack >= 0.5).astype(int)

    print("\n" + "=" * 60)
    print("Test Set  AUC-ROC")
    print("=" * 60)
    print(f"  XGBoost      : {roc_auc_score(y_test, p_xgb_te):.4f}")
    print(f"  LightGBM     : {roc_auc_score(y_test, p_lgbm_te):.4f}")
    print(f"  RandomForest : {roc_auc_score(y_test, p_rf_te):.4f}")
    print(f"  Stacking     : {roc_auc_score(y_test, p_stack):.4f}  <-- meta")
    print("=" * 60)
    print(f"\nAverage Precision (Stacking): {average_precision_score(y_test, p_stack):.4f}")
    print("\nClassification Report (Stacking, threshold=0.50):")
    print(classification_report(y_test, preds, target_names=["정시(0)", "지연(1)"]))

    # ── 아티팩트 저장 ──────────────────────────────────────────────────────────
    artifact = {
        "xgb": xgb, "lgbm": lgbm, "rf": rf, "meta": meta,
        "te_rf": te, "cat_vocab": cat_vocab,
        "meta_coef": coef,
    }
    out_path = os.path.join(MODELS_DIR, STACK_MODEL_FILE)
    joblib.dump(artifact, out_path)
    print(f"\n스태킹 모델 저장: {out_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--full", action="store_true", help="전체 데이터 사용")
    args = parser.parse_args()
    train_stacking(use_full=args.full)
