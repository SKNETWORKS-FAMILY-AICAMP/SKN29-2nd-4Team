"""Entry point: train → evaluate.

Run from the rev_02 directory:
    python run.py
"""
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["MKL_THREADING_LAYER"] = "INTEL"
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("MKL_NUM_THREADS", "4")

from ml.rev_02.train import run_training
from ml.rev_02.evaluate import run_evaluation


def main():
    print("=" * 65)
    print("Rev_02  Two-Stage FCNN  --  Full Pipeline")
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
