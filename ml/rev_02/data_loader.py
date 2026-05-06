import pickle
import numpy as np
import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder, StandardScaler

from ml.rev_02.config import (
    TRAIN_FILE, TEST_FILE, TARGET, BINARY_MODE,
    STATIC_NUM_FEATURES, STATIC_CAT_FEATURES, DYNAMIC_FEATURES,
    BATCH_SIZE, POS_WEIGHT_MUL,
)


class FlightDataset(Dataset):
    def __init__(
        self,
        static_num: np.ndarray,
        static_cat: np.ndarray,
        dynamic:    np.ndarray,
        labels:     np.ndarray,
    ):
        self.static_num = torch.tensor(static_num, dtype=torch.float32)
        self.static_cat = torch.tensor(static_cat, dtype=torch.long)
        self.dynamic    = torch.tensor(dynamic,    dtype=torch.float32)
        self.labels     = torch.tensor(labels,     dtype=torch.float32)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return (
            self.static_num[idx],
            self.static_cat[idx],
            self.dynamic[idx],
            self.labels[idx],
        )


def load_and_preprocess(
    train_path=None,
    test_path=None,
    fit: bool = True,
    scaler: StandardScaler = None,
    label_encoders: dict   = None,
):
    """Load, encode, and scale data.

    Parameters
    ----------
    fit : bool
        True  → fit scaler and label_encoders on train data (first run).
        False → use provided scaler/label_encoders (for evaluation).

    Returns
    -------
    train_ds, test_ds, scaler, label_encoders, vocab_sizes, pos_weight
    """
    train_path = train_path or TRAIN_FILE
    test_path  = test_path  or TEST_FILE

    df_tr = pd.read_csv(train_path)
    df_te = pd.read_csv(test_path)

    # ── Target ────────────────────────────────────────────────────────────────
    if BINARY_MODE:
        y_tr = (df_tr[TARGET] > 0).astype(int).values
        y_te = (df_te[TARGET] > 0).astype(int).values
    else:
        y_tr = df_tr[TARGET].values.astype(int)
        y_te = df_te[TARGET].values.astype(int)

    # ── Categorical encoding (LabelEncoder) ───────────────────────────────────
    if fit:
        label_encoders = {}
        for col in STATIC_CAT_FEATURES:
            le = LabelEncoder()
            combined = pd.concat([df_tr[col], df_te[col]], axis=0).astype(str)
            le.fit(combined)
            label_encoders[col] = le

    for col in STATIC_CAT_FEATURES:
        le = label_encoders[col]
        df_tr[col] = le.transform(df_tr[col].astype(str))
        df_te[col] = le.transform(df_te[col].astype(str))

    # ── Numerical scaling ─────────────────────────────────────────────────────
    all_num = STATIC_NUM_FEATURES + DYNAMIC_FEATURES
    if fit:
        scaler = StandardScaler()
        scaler.fit(df_tr[all_num])

    tr_num = scaler.transform(df_tr[all_num])
    te_num = scaler.transform(df_te[all_num])

    ns = len(STATIC_NUM_FEATURES)
    tr_s_num, tr_dyn = tr_num[:, :ns], tr_num[:, ns:]
    te_s_num, te_dyn = te_num[:, :ns], te_num[:, ns:]

    tr_s_cat = df_tr[STATIC_CAT_FEATURES].values
    te_s_cat = df_te[STATIC_CAT_FEATURES].values

    vocab_sizes = {col: len(label_encoders[col].classes_) for col in STATIC_CAT_FEATURES}

    # ── pos_weight for BCEWithLogitsLoss ──────────────────────────────────────
    pos_weight = None
    if BINARY_MODE:
        n_neg = int((y_tr == 0).sum())
        n_pos = int((y_tr == 1).sum())
        ratio = n_neg / max(n_pos, 1) * POS_WEIGHT_MUL
        pos_weight = torch.tensor([ratio], dtype=torch.float32)
        print(f"  pos_weight = {ratio:.3f}  (neg={n_neg:,}  pos={n_pos:,})")

    train_ds = FlightDataset(tr_s_num, tr_s_cat, tr_dyn, y_tr)
    test_ds  = FlightDataset(te_s_num, te_s_cat, te_dyn, y_te)

    return train_ds, test_ds, scaler, label_encoders, vocab_sizes, pos_weight


def make_loaders(
    train_ds: FlightDataset,
    test_ds:  FlightDataset,
    batch_size: int = BATCH_SIZE,
):
    train_loader = DataLoader(
        train_ds,
        batch_size=batch_size,
        shuffle=True,
        num_workers=0,
        pin_memory=True,
    )
    test_loader = DataLoader(
        test_ds,
        batch_size=batch_size * 2,
        shuffle=False,
        num_workers=0,
        pin_memory=True,
    )
    return train_loader, test_loader
