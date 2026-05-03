from pathlib import Path

BASE_DIR   = Path(__file__).resolve().parents[3]
DATA_DIR   = BASE_DIR / "data" / "minibatch_binary"
OUTPUT_DIR = BASE_DIR / "data" / "outputs" / "rev_03"

TRAIN_FILE = DATA_DIR / "minibatch_flight_delay_train_clean.csv"
TEST_FILE  = DATA_DIR / "minibatch_flight_delay_test_clean.csv"

TARGET      = "DelayCategory"
BINARY_MODE = True

# ── Features ──────────────────────────────────────────────────────────────────
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

# ── Embeddings: 공항(376종)은 표현력 확대 ──────────────────────────────────────
EMB_DIM = {
    "Marketing_Airline_Network": 16,
    "Operating_Airline":         16,
    "Origin":                    32,
    "Dest":                      32,
}

# ── Model ─────────────────────────────────────────────────────────────────────
STATIC_HIDDEN  = [512, 256, 128]   # output dim = 128
DYNAMIC_HIDDEN = [512, 256, 128]   # + linear head → 1
DROPOUT        = 0.25

# ── Focal Loss ────────────────────────────────────────────────────────────────
# alpha: 양성(지연) 클래스 가중치, gamma: hard example 집중 강도
FOCAL_ALPHA = 0.75
FOCAL_GAMMA = 2.0

# ── Training ──────────────────────────────────────────────────────────────────
BATCH_SIZE   = 4096
LR           = 3e-4
WEIGHT_DECAY = 1e-4
MAX_EPOCHS   = 200
PATIENCE     = 15
SEED         = 42

# CosineAnnealingWarmRestarts: T_0 epoch마다 LR 재시작 → local minimum 탈출
T_RESTART    = 30

# ── Artifacts ─────────────────────────────────────────────────────────────────
MODEL_PATH   = OUTPUT_DIR / "best_model.pt"
SCALER_PATH  = OUTPUT_DIR / "scaler.pkl"
ENCODER_PATH = OUTPUT_DIR / "label_encoders.pkl"
