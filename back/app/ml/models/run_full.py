"""
Full Data Pipeline
  1. HPO          -- 미니배치 샘플로 하이퍼파라미터 탐색 (빠른 실행)
  2. Train full   -- 전체 데이터로 XGBoost / LightGBM / RandomForest 학습
  3. Stacking     -- 전체 데이터 blending stacking (meta = LogisticRegression)
  4. Evaluation   -- 전체 테스트 데이터로 AUC-ROC 비교

Usage:
  python run_full.py            # 전체 실행
  python run_full.py --skip-hpo # HPO 결과 재사용 (학습부터 시작)
"""
import subprocess
import sys
import os
import time
import datetime


def run(cmd: str, name: str) -> float:
    print(f"\n{'=' * 60}")
    print(f"  {name}")
    print(f"  시작: {datetime.datetime.now().strftime('%H:%M:%S')}")
    print(f"{'=' * 60}")
    start = time.time()
    process = subprocess.Popen(cmd, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    elapsed = time.time() - start
    if process.returncode != 0:
        print(f"\n[ERROR] '{name}' 실패 (exit={process.returncode}) -- 파이프라인 중단")
        sys.exit(1)
    print(f"\n  완료: {name}  ({elapsed:.0f}s = {elapsed / 60:.1f}min)")
    return elapsed


def main():
    skip_hpo = "--skip-hpo" in sys.argv
    p = os.path.dirname(os.path.abspath(__file__))

    def s(name):
        return os.path.join(p, name)

    hpo_steps = [] if skip_hpo else [
        ("XGBoost  HPO",      f"python \"{s('train_xgboost.py')}\" hpo"),
        ("LightGBM HPO",      f"python \"{s('train_lgbm.py')}\" hpo"),
        ("RandomForest HPO",  f"python \"{s('train_rf.py')}\" hpo"),
    ]

    train_steps = [
        ("XGBoost  Train (full)",      f"python \"{s('train_xgboost.py')}\" train_full"),
        ("LightGBM Train (full)",      f"python \"{s('train_lgbm.py')}\" train_full"),
        ("RandomForest Train (full)",  f"python \"{s('train_rf.py')}\" train_full"),
        ("Stacking (full data)",       f"python \"{s('train_stacking.py')}\" --full"),
        ("Evaluation (full test set)", f"python \"{s('evaluate.py')}\" --full"),
    ]

    steps = hpo_steps + train_steps

    print("\n" + "=" * 60)
    print("  Full Data Pipeline  --  Start")
    if skip_hpo:
        print("  (HPO skipped -- saved params 재사용)")
    print(f"  시작 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  총 {len(steps)}단계")
    print("=" * 60)

    timings = []
    for name, cmd in steps:
        elapsed = run(cmd, name)
        timings.append((name, elapsed))

    total = sum(t for _, t in timings)
    print("\n" + "=" * 60)
    print("  Pipeline 완료!")
    print(f"  종료 시각: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)
    for name, t in timings:
        print(f"  {name:35s} {t:6.0f}s ({t/60:.1f}min)")
    print("-" * 60)
    print(f"  총 소요 시간: {total:.0f}s = {total/60:.1f}min = {total/3600:.1f}h")
    print("=" * 60)


if __name__ == "__main__":
    main()
