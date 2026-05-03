import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["MKL_THREADING_LAYER"] = "INTEL"
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

import pickle
import sys
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import roc_auc_score, f1_score

from config import (
    OUTPUT_DIR, STATIC_NUM_FEATURES, DYNAMIC_FEATURES,
    BATCH_SIZE, LR, WEIGHT_DECAY, MAX_EPOCHS, PATIENCE, SEED,
    T_RESTART, MODEL_PATH, SCALER_PATH, ENCODER_PATH,
)
from data_loader import load_and_preprocess, make_loaders
from model import TwoStageFCNN, FocalLoss

try:
    from tqdm import tqdm
    _has_tqdm = True
except ImportError:
    _has_tqdm = False


def _iter(loader, desc=""):
    if _has_tqdm:
        return tqdm(loader, desc=desc, leave=False, file=sys.stdout)
    return loader


def _train_epoch(model, loader, optimizer, criterion, device) -> float:
    model.train()
    total_loss = 0.0
    for s_num, s_cat, dyn, y in _iter(loader, "train"):
        s_num, s_cat, dyn, y = (
            s_num.to(device), s_cat.to(device), dyn.to(device), y.to(device)
        )
        logits = model(s_num, s_cat, dyn)
        loss   = criterion(logits, y)
        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        optimizer.step()
        total_loss += loss.item() * len(y)
    return total_loss / len(loader.dataset)


@torch.no_grad()
def _eval_epoch(model, loader, criterion, device):
    model.eval()
    total_loss = 0.0
    all_logits, all_labels = [], []
    for s_num, s_cat, dyn, y in _iter(loader, "eval"):
        s_num, s_cat, dyn, y = (
            s_num.to(device), s_cat.to(device), dyn.to(device), y.to(device)
        )
        logits = model(s_num, s_cat, dyn)
        loss   = criterion(logits, y)
        total_loss += loss.item() * len(y)
        all_logits.append(logits.cpu())
        all_labels.append(y.cpu())

    logits = torch.cat(all_logits).numpy()
    labels = torch.cat(all_labels).numpy()
    probs  = torch.sigmoid(torch.from_numpy(logits)).numpy()
    return total_loss / len(loader.dataset), probs, labels


def run_training():
    torch.manual_seed(SEED)
    np.random.seed(SEED)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Loading data ...")
    train_ds, test_ds, scaler, encoders, vocab_sizes = load_and_preprocess()
    train_loader, test_loader = make_loaders(train_ds, test_ds, BATCH_SIZE)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Device     : {device}")
    print(f"Train rows : {len(train_ds):,}   |   Test rows : {len(test_ds):,}")

    model = TwoStageFCNN(
        vocab_sizes=vocab_sizes,
        n_static_num=len(STATIC_NUM_FEATURES),
        n_dynamic=len(DYNAMIC_FEATURES),
    ).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    print(f"Parameters : {n_params:,}\n")

    criterion = FocalLoss()
    optimizer = optim.AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    # CosineAnnealingWarmRestarts: restart every T_RESTART epochs to escape local minima
    scheduler = optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=T_RESTART, T_mult=1, eta_min=1e-6
    )

    best_auc     = 0.0
    patience_cnt = 0

    print(f"Training up to {MAX_EPOCHS} epochs (early-stop patience={PATIENCE}) ...")
    print("-" * 75)

    for epoch in range(1, MAX_EPOCHS + 1):
        tr_loss = _train_epoch(model, train_loader, optimizer, criterion, device)
        va_loss, probs, labels = _eval_epoch(model, test_loader, criterion, device)

        auc    = roc_auc_score(labels, probs)
        preds  = (probs >= 0.5).astype(int)
        f1     = f1_score(labels, preds, average="binary", zero_division=0)
        lr_now = optimizer.param_groups[0]["lr"]

        print(
            f"Epoch {epoch:3d} | "
            f"train_loss={tr_loss:.4f}  val_loss={va_loss:.4f}  "
            f"AUC={auc:.4f}  F1={f1:.4f}  lr={lr_now:.2e}"
        )

        scheduler.step(epoch - 1)

        if auc > best_auc:
            best_auc     = auc
            patience_cnt = 0
            torch.save(
                {
                    "epoch":        epoch,
                    "model_state":  model.state_dict(),
                    "vocab_sizes":  vocab_sizes,
                    "n_static_num": len(STATIC_NUM_FEATURES),
                    "n_dynamic":    len(DYNAMIC_FEATURES),
                    "best_auc":     best_auc,
                },
                MODEL_PATH,
            )
            print(f"  -> Saved best model (AUC={best_auc:.4f})")
        else:
            patience_cnt += 1
            if patience_cnt >= PATIENCE:
                print(f"\nEarly stopping at epoch {epoch}  (best AUC={best_auc:.4f})")
                break

    with open(SCALER_PATH,  "wb") as f:
        pickle.dump(scaler,   f)
    with open(ENCODER_PATH, "wb") as f:
        pickle.dump(encoders, f)

    print(f"\nBest AUC-ROC : {best_auc:.4f}")
    print(f"Artifacts saved to {OUTPUT_DIR}")
    return model, vocab_sizes


if __name__ == "__main__":
    run_training()
