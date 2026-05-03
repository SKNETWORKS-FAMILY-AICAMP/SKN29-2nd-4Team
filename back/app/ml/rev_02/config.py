from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parents[3]   # c:\prj2\back
DATA_DIR   = BASE_DIR / "data" / "minibatch_binary"
OUTPUT_DIR = BASE_DIR / "data" / "outputs" / "rev_02"

TRAIN_FILE = DATA_DIR / "minibatch_flight_delay_train_clean.csv"
TEST_FILE  = DATA_DIR / "minibatch_flight_delay_test_clean.csv"

TARGET      = "DelayCategory"
BINARY_MODE = True   # True: 0=정시, 1=지연 (DelayCategory > 0)

# ── Feature definitions ───────────────────────────────────────────────────────
# 비행 전 확정되는 정적 정보 (스케줄, 노선, 항공사)
STATIC_NUM_FEATURES = [
    "Month", "DayofMonth", "DayOfWeek", "is_weekend",
    "month_sin", "month_cos",
    "CRSDep_sin", "CRSDep_cos", "CRSArr_sin", "CRSArr_cos",
    "CRSElapsedTime", "is_codeshare",
]

STATIC_CAT_FEATURES = [
    "Marketing_Airline_Network",
    "Operating_Airline",
    "Origin",
    "Dest",
]

# 당일 실시간 정보 (기상, 운영 지표)
DYNAMIC_FEATURES = [
    "origin_precipitation_mm", "origin_snowfall_cm",
    "origin_windspeed_max_kmh", "origin_windgusts_max_kmh",
    "dest_precipitation_mm",   "dest_snowfall_cm",
    "dest_windspeed_max_kmh",  "dest_windgusts_max_kmh",
    "origin_temp_max_c",       "origin_cloudcover_mean_pct",
    "dest_temp_max_c",         "dest_cloudcover_mean_pct",
    "origin_has_precip",       "dest_has_precip",
    "origin_has_snow",         "dest_has_snow",
    "origin_taxiout_mean",     "origin_hour_taxiout_mean",
    "dest_taxiin_mean",        "dest_hour_taxiin_mean",
    "expected_elapsed_over_schedule", "expected_elapsed_hour_over_schedule",
]

# Embedding dim per categorical feature
EMB_DIM = {
    "Marketing_Airline_Network": 8,
    "Operating_Airline":         8,
    "Origin":                   16,
    "Dest":                     16,
}

# ── Model architecture ────────────────────────────────────────────────────────
STATIC_HIDDEN  = [256, 128, 64]   # last elem = static repr dim passed to DynamicFCNN
DYNAMIC_HIDDEN = [256, 128, 64]   # last elem before final linear head
DROPOUT        = 0.3

# ── Training ──────────────────────────────────────────────────────────────────
BATCH_SIZE     = 2048
LR             = 1e-3
WEIGHT_DECAY   = 1e-4
MAX_EPOCHS     = 300
PATIENCE       = 10     # early-stop patience (by val AUC-ROC)
SEED           = 42
POS_WEIGHT_MUL = 1.5   # multiplier on neg/pos ratio for BCEWithLogitsLoss

# ── Saved artifact paths ──────────────────────────────────────────────────────
MODEL_PATH   = OUTPUT_DIR / "best_model.pt"
SCALER_PATH  = OUTPUT_DIR / "scaler.pkl"
ENCODER_PATH = OUTPUT_DIR / "label_encoders.pkl"
