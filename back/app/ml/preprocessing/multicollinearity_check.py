import pandas as pd
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.tools.tools import add_constant

COLLINEAR_FEATURES = [
    "expected_elapsed_mean",
    "expected_elapsed_hour_mean",
    "schedule_buffer_hour",
    "schedule_buffer",
    "route_hour_airtime_mean",
    "route_airtime_mean",
    "origin_temp_mean_c",
    "origin_temp_min_c",
    "dest_temp_mean_c",
    "dest_temp_min_c",
    "Distance",
    "FlightDate"
]


def check_vif(csv_path: str, target_col: str = None, sample_size: int = 30000, drop_cols: list = None) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    X = df.select_dtypes(include=["number"])

    exclude = [c for c in (drop_cols or []) + ([target_col] if target_col else []) if c in X.columns]
    X = X.drop(columns=exclude).dropna()

    if len(X) > sample_size:
        X = X.sample(n=sample_size, random_state=42)

    X = add_constant(X)

    vif = pd.DataFrame({
        "Feature": X.columns,
        "VIF": [variance_inflation_factor(X.values, i) for i in range(len(X.columns))],
    })
    return vif.sort_values("VIF", ascending=False).reset_index(drop=True)


if __name__ == "__main__":
    import sys
    
    # 기본 경로 설정
    default_csv = r"C:\proj2\back\data\processed\rev_01\flight_delay_train_clean.csv"
    default_target = "ArrDelayMinutes"

    if len(sys.argv) < 2:
        print(f"인자가 없어 기본 파일로 실행합니다:\n{default_csv}")
        csv_path = default_csv
        target_col = default_target
    else:
        csv_path = sys.argv[1]
        target_col = sys.argv[2] if len(sys.argv) > 2 else None
        
    result = check_vif(csv_path, target_col=target_col, drop_cols=COLLINEAR_FEATURES)
    print(result)
