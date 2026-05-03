"""
Tree Stacking Pipeline

실행 순서:
  1. HPO  (XGBoost / LightGBM / RandomForest)  -- 이미 완료했으면 skip 가능
  2. Train (미니배치 전체, 각 모델 개별 저장)
  3. Stacking (blending meta-learner 학습)
  4. Evaluate (개별 모델 + 스태킹 성능 비교)

Usage:
  python run_preliminary.py          # HPO + Train + Stack + Eval
  python run_preliminary.py --skip-hpo  # Train + Stack + Eval (HPO 결과 재사용)
"""
import subprocess
import sys
import os
import time


def run_command(command: str, task_name: str) -> bool:
    process = subprocess.Popen(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    return process.returncode == 0


def main():
    skip_hpo  = "--skip-hpo" in sys.argv
    models_path = os.path.dirname(os.path.abspath(__file__))

    def script(name):
        return os.path.join(models_path, name)

    hpo_steps = [] if skip_hpo else [
        ("XGBoost  HPO",      f"python {script('train_xgboost.py')} hpo"),
        ("LightGBM HPO",      f"python {script('train_lgbm.py')} hpo"),
        ("RandomForest HPO",  f"python {script('train_rf.py')} hpo"),
    ]

    steps = hpo_steps + [
        ("XGBoost  Train",    f"python {script('train_xgboost.py')} train_mini"),
        ("LightGBM Train",    f"python {script('train_lgbm.py')} train_mini"),
        ("RandomForest Train",f"python {script('train_rf.py')} train_mini"),
        ("Stacking",          f"python {script('train_stacking.py')}"),
        ("Evaluation",        f"python {script('evaluate.py')}"),
    ]

    print("\n" + "=" * 60)
    print("Tree Stacking Pipeline  --  Start")
    if skip_hpo:
        print("  (HPO skipped -- reusing saved params)")
    print("=" * 60)

    for task_name, cmd in steps:
        print(f"\n>>> {task_name}")
        start = time.time()
        if not run_command(cmd, task_name):
            print(f"\n[ERROR] {task_name} 실패 -- 파이프라인 중단")
            sys.exit(1)
        print(f">>> {task_name} done ({time.time() - start:.1f}s)")

    print("\n" + "=" * 60)
    print("Pipeline finished.")
    print("=" * 60)


if __name__ == "__main__":
    main()
