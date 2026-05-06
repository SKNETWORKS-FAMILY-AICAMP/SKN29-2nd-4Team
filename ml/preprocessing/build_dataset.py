import os
import sys
import glob
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ml.preprocessing.multicollinearity_check import COLLINEAR_FEATURES

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data"))
REV01_DIR = os.path.join(BASE_DIR, "processed", "rev_01")
REV02_DIR = os.path.join(BASE_DIR, "processed", "rev_02")
MINIBATCH_DIR = os.path.join(BASE_DIR, "minibatch")


def categorize_delay(series: pd.Series) -> pd.Series:
    conditions = [
        series <= 0,
        (series > 0) & (series <= 15),
        (series > 15) & (series < 180),
        series >= 180,
    ]
    return pd.Series(np.select(conditions, [0, 1, 2, 3], default=3), index=series.index)


def build_rev02():
    """rev_01의 모든 CSV에서 다중공선성 컬럼 제거 + 타겟 범주화 → rev_02에 저장"""
    os.makedirs(REV02_DIR, exist_ok=True)
    csv_files = glob.glob(os.path.join(REV01_DIR, "*.csv"))

    if not csv_files:
        print(f"rev_01에 CSV 파일이 없습니다: {REV01_DIR}")
        return

    for path in csv_files:
        name = os.path.basename(path)
        df = pd.read_csv(path)

        cols_to_drop = [c for c in COLLINEAR_FEATURES if c in df.columns]
        df.drop(columns=cols_to_drop, inplace=True)

        if "ArrDelayMinutes" in df.columns:
            df["DelayCategory"] = categorize_delay(df["ArrDelayMinutes"])
            df.drop(columns=["ArrDelayMinutes"], inplace=True)

        df.to_csv(os.path.join(REV02_DIR, name), index=False)
        print(f"[rev_02] {name}: {len(df)} rows, {len(df.columns)} cols")


def build_minibatch(frac: float = 0.1):
    """rev_02의 모든 CSV에서 10% 샘플링 → minibatch에 저장"""
    os.makedirs(MINIBATCH_DIR, exist_ok=True)
    csv_files = glob.glob(os.path.join(REV02_DIR, "*.csv"))

    if not csv_files:
        print(f"rev_02에 CSV 파일이 없습니다: {REV02_DIR}")
        return

    for path in csv_files:
        name = os.path.basename(path)
        dst_name = f"minibatch_{name}"
        df = pd.read_csv(path)
        sample = df.sample(frac=frac, random_state=42)
        sample.to_csv(os.path.join(MINIBATCH_DIR, dst_name), index=False)

        print(f"[minibatch] {dst_name}: {len(sample)} rows")
        if "DelayCategory" in sample.columns:
            print(sample["DelayCategory"].value_counts().sort_index())


if __name__ == "__main__":
    build_rev02()
    build_minibatch()
