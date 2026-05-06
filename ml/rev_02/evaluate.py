import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["MKL_THREADING_LAYER"] = "INTEL"
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

import pickle
import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.metrics import (
    roc_auc_score,
    average_precision_score,
    f1_score,
    precision_score,
    recall_score,
    confusion_matrix,
    classification_report,
)

from ml.rev_02.config import (
    OUTPUT_DIR, STATIC_NUM_FEATURES, DYNAMIC_FEATURES,
    MODEL_PATH, SCALER_PATH, ENCODER_PATH, BATCH_SIZE,
)
from ml.rev_02.data_loader import load_and_preprocess
from ml.rev_02.model import TwoStageFCNN


def _find_best_threshold(probs: np.ndarray, labels: np.ndarray, metric: str = "f1"):
    """Sweep thresholds [0.20, 0.80] to maximise the chosen metric."""
    best_thr, best_val = 0.5, 0.0
    for thr in np.arange(0.20, 0.81, 0.01):
        preds = (probs >= thr).astype(int)
        val = (
            f1_score(labels, preds, average="binary", zero_division=0)
            if metric == "f1"
            else recall_score(labels, preds, zero_division=0)
        )
        if val > best_val:
            best_val, best_thr = val, float(thr)
    return best_thr, best_val


def run_evaluation(
    model_path=None,
    scaler_path=None,
    encoder_path=None,
):
    model_path   = model_path   or MODEL_PATH
    scaler_path  = scaler_path  or SCALER_PATH
    encoder_path = encoder_path or ENCODER_PATH

    print("Loading saved artifacts ...")
    ckpt = torch.load(model_path, map_location="cpu", weights_only=False)
    with open(scaler_path,  "rb") as f:
        scaler   = pickle.load(f)
    with open(encoder_path, "rb") as f:
        encoders = pickle.load(f)

    print("Preprocessing test data ...")
    _, test_ds, *_ = load_and_preprocess(fit=False, scaler=scaler, label_encoders=encoders)
    test_loader = DataLoader(
        test_ds, batch_size=BATCH_SIZE * 2, shuffle=False, num_workers=0
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = TwoStageFCNN(
        vocab_sizes=ckpt["vocab_sizes"],
        n_static_num=ckpt["n_static_num"],
        n_dynamic=ckpt["n_dynamic"],
    ).to(device)
    model.load_state_dict(ckpt["model_state"])
    model.eval()
    print(f"Loaded model from epoch {ckpt['epoch']}  (best AUC={ckpt['best_auc']:.4f})\n")

    all_logits, all_labels = [], []
    with torch.no_grad():
        for s_num, s_cat, dyn, y in test_loader:
            logits = model(s_num.to(device), s_cat.to(device), dyn.to(device))
            all_logits.append(logits.cpu())
            all_labels.append(y)

    logits = torch.cat(all_logits).numpy()
    labels = torch.cat(all_labels).numpy()
    probs  = torch.sigmoid(torch.from_numpy(logits)).numpy()

    # ── Metrics ───────────────────────────────────────────────────────────────
    auc      = roc_auc_score(labels, probs)
    ap       = average_precision_score(labels, probs)

    best_thr_f1, best_f1 = _find_best_threshold(probs, labels, "f1")
    preds_f1 = (probs >= best_thr_f1).astype(int)
    prec_f1  = precision_score(labels, preds_f1, zero_division=0)
    rec_f1   = recall_score(labels, preds_f1, zero_division=0)

    default_preds = (probs >= 0.5).astype(int)

    report_lines = [
        "=" * 65,
        "Rev_02  Two-Stage FCNN  --  Evaluation Report",
        "=" * 65,
        "",
        f"  AUC-ROC              : {auc:.4f}",
        f"  Average Precision    : {ap:.4f}   (area under PR curve)",
        "",
        f"  [ threshold = {best_thr_f1:.2f} -- optimised for F1 ]",
        f"  F1   (binary)        : {best_f1:.4f}",
        f"  Precision            : {prec_f1:.4f}",
        f"  Recall               : {rec_f1:.4f}",
        "",
        "  Classification Report (threshold=0.50):",
        classification_report(
            labels, default_preds,
            target_names=["정시(0)", "지연(1)"],
        ),
        f"  Classification Report (threshold={best_thr_f1:.2f}, best F1):",
        classification_report(
            labels, preds_f1,
            target_names=["정시(0)", "지연(1)"],
        ),
        "  Confusion Matrix (rows=actual, cols=pred) @ best threshold:",
        str(confusion_matrix(labels, preds_f1)),
        "",
        "=" * 65,
    ]

    output = "\n".join(report_lines)
    print(output)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / "evaluation_report.txt"
    out_path.write_text(output, encoding="utf-8")
    print(f"\nReport → {out_path}")

    return auc, best_f1


if __name__ == "__main__":
    run_evaluation()
