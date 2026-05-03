"""Entry point: train -> evaluate.

Run from the rev_03 directory:
    python run.py
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["MKL_THREADING_LAYER"] = "INTEL"
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

from train import run_training
from evaluate import run_evaluation


def main():
    print("=" * 65)
    print("Rev_03  Two-Stage FCNN (Focal Loss)  --  Full Pipeline")
    print("=" * 65)
    print()

    run_training()

    print()
    print("=" * 65)
    print("Evaluating on test set...")
    print("=" * 65)
    print()

    run_evaluation()


if __name__ == "__main__":
    main()
