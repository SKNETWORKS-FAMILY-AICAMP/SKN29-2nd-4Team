import subprocess
import sys
import os
import time
from tqdm import tqdm

def run_command(command, task_name):
    # 하위 프로세스의 출력을 실시간으로 터미널에 표시하여 tqdm이 보이게 함
    process = subprocess.Popen(command, shell=True, stdout=sys.stdout, stderr=sys.stderr)
    process.wait()
    return process.returncode == 0

def main():
    models_path = os.path.dirname(os.path.abspath(__file__))
    
    scripts = [
        ("XGBoost", f"python {os.path.join(models_path, 'train_xgboost.py')} train_mini"),
        ("LightGBM", f"python {os.path.join(models_path, 'train_lgbm.py')} train_mini"),
        ("RandomForest", f"python {os.path.join(models_path, 'train_rf.py')} train_mini"),
        ("Evaluation", f"python {os.path.join(models_path, 'evaluate.py')}")
    ]
    
    print("\nStarting Pipeline...")
    
    for task_name, cmd in scripts:
        print(f"\n>>> Task: {task_name}")
        start_time = time.time()
        
        success = run_command(cmd, task_name)
        
        if not success:
            print(f"\nError occurred during: {task_name}")
            break
            
        elapsed = time.time() - start_time
        print(f">>> {task_name} finished in {elapsed:.1f}s")
        
    print("\nPipeline execution finished.")

if __name__ == "__main__":
    main()
