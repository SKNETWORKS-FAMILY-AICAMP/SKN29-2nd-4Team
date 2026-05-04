#  산출물 3: 모델 메타데이터

---

## 모델 1: XGBoost Classifier (최고 성능 트리 모델)

### 기본 정보

| 항목 | 내용 |
|------|------|
| 모델명 | XGBoost Classifier |
| 버전 | v1.0.0 |
| 과제 | 항공편 지연 이진 분류 (Flight Delay Binary Prediction) |
| 타겟 | `DelayCategory` → 이진화 (0: 정시, 1: 지연) |
| 이진화 기준 | `DelayCategory > 0` → 지연(1) |

---

### 학습 환경

| 라이브러리 | 버전 | 비고 |
|-----------|------|------|
| Python | 3.11 | cpython-311 캐시 확인 |
| scikit-learn | 1.0+ | TargetEncoder, classification_report 사용 |
| xgboost | 1.5+ | enable_categorical=True 지원 버전 |
| lightgbm | 3.0+ | early_stopping / log_evaluation 콜백 지원 |
| torch | 1.9+ | FCNN 학습 사용 |
| pandas | 1.1+ | CategoricalDtype 지원 버전 |
| numpy | 1.19+ | 수치 연산 |
| optuna | 2.0+ | create_study / suggest_* API 사용 |
| joblib | 1.0+ | 모델 직렬화 |

---

### 모델 성능 (최종, Test 기준)

**테스트 데이터**: `data/processed/rev_03/flight_delay_test_clean.csv`  
**샘플 수**: 929,965건 (정시 626,834 / 지연 303,131)

#### 전체 지표

| 지표 | 값 |
|------|-----|
| ROC-AUC | **0.8437** |
| Average Precision | 0.5356 |
| Accuracy | 0.70 |

#### 클래스별 성능

| 클래스 | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| 정시(0) | 0.74 | 0.85 | 0.79 | 626,834 |
| 지연(1) | 0.55 | 0.39 | 0.46 | 303,131 |
| macro avg | 0.65 | 0.62 | 0.63 | 929,965 |
| weighted avg | 0.68 | 0.70 | 0.68 | 929,965 |

#### 혼동 행렬

|  | 예측: 정시(0) | 예측: 지연(1) |
|--|-------------|-------------|
| **실제: 정시(0)** | 530,361 (TN) | 96,473 (FP) |
| **실제: 지연(1)** | 183,728 (FN) | 119,403 (TP) |

#### 경쟁 모델 비교

| 모델 | ROC-AUC | Avg Precision | Accuracy |
|------|---------|-------------|---------|
| **XGBoost ✅** | **0.8437** | **0.5356** | 0.70 |
| Stacking | 0.8412 | 0.5326 | 0.71 |
| LightGBM | 0.8376 | 0.5244 | 0.69 |
| RandomForest | 0.8278 | 0.5135 | 0.67 |

---

### 하이퍼파라미터

#### 고정 파라미터

| 파라미터 | 값 |
|---------|-----|
| objective | binary:logistic |
| eval_metric | logloss |
| tree_method | hist |
| enable_categorical | True |
| early_stopping_rounds | 50 |
| random_state | 42 |
| n_jobs | -1 |

#### HPO 탐색 파라미터 (Optuna, 70 trials, 최적화 목표: ROC-AUC)

| 파라미터 | 탐색 범위 |
|---------|---------|
| n_estimators | 100 ~ 1,000 |
| max_depth | 3 ~ 10 |
| learning_rate | 0.01 ~ 0.30 (log scale) |
| subsample | 0.6 ~ 1.0 |
| colsample_bytree | 0.6 ~ 1.0 |
| min_child_weight | 1 ~ 10 |
| reg_lambda | 0.001 ~ 10.0 (log scale) |

---

### 입력 데이터 스펙

#### 정적 특성 (Static, 16개) — 비행 출발 전 확정, 당일 변화 없음

| 유형 | 특성 수 | 특성명 |
|------|--------|--------|
| 수치형 | 12 | Month, DayofMonth, DayOfWeek, is_weekend, month_sin, month_cos, CRSDep_sin, CRSDep_cos, CRSArr_sin, CRSArr_cos, CRSElapsedTime, is_codeshare |
| 범주형 | 4 | Marketing_Airline_Network, Operating_Airline, Origin, Dest |

#### 동적 특성 (Dynamic, 22개) — 운항 당일 실시간 변화

| 유형 | 특성 수 | 특성명 |
|------|--------|--------|
| 기상 (출발지/도착지) | 16 | origin/dest: precipitation_mm, snowfall_cm, windspeed_max_kmh, windgusts_max_kmh, temp_max_c, cloudcover_mean_pct, has_precip, has_snow |
| 운영 지연 지표 | 4 | origin_taxiout_mean, origin_hour_taxiout_mean, dest_taxiin_mean, dest_hour_taxiin_mean |
| 스케줄 편차 | 2 | expected_elapsed_over_schedule, expected_elapsed_hour_over_schedule |

#### 전처리 방법

| 특성 유형 | 전처리 방법 |
|---------|-----------|
| 범주형 4종 | pandas CategoricalDtype (어휘: train+test 합집합 정렬) |
| 수치형 34종 | 없음 — XGBoost는 스케일 무관 |
| 클래스 불균형 | 클래스 가중치 √(n / (2 × count[c])) 적용 |

#### 제거된 특성 (다중공선성, VIF 기반)

```
expected_elapsed_mean, expected_elapsed_hour_mean,
schedule_buffer_hour, schedule_buffer,
route_hour_airtime_mean, route_airtime_mean,
origin_temp_mean_c, origin_temp_min_c,
dest_temp_mean_c, dest_temp_min_c,
Distance, FlightDate
```

---

### 예측값 해석

| 출력값 | 의미 |
|--------|------|
| `predict(X) == 0` | 정시 도착 예측 |
| `predict(X) == 1` | 지연 도착 예측 |
| `predict_proba(X)[:, 1]` | 지연 확률 (0.0 ~ 1.0) |


---

### 모니터링 및 재학습

| 항목 | 내용 |
|------|------|
| 드리프트 감지 기준 | ROC-AUC < **0.80** |
| 재학습 방식 | 증분 학습 (`xgb_model=model.get_booster()`) |

---

### 모델 한계점

| 항목 | 내용 |
|------|------|
| 지연 Recall | 0.39 — 실제 지연의 약 61%를 미탐지 |
| 임계값 고정 | 기본 0.5 적용 — 시나리오별 최적 임계값 미탐색 |

> Recall 향상이 필요한 경우: RandomForest (지연 Recall 0.50) 또는 FCNN rev_03 (Focal Loss 적용, 학습 예정) 고려

---

## 모델 2: FCNN (정적/동적 이중 브랜치 딥러닝 모델)

### 기본 정보

| 항목 | 내용 |
|------|------|
| 모델명 | FCNN (Two-Stage Fully Connected Neural Network) |
| 버전 | v1.0.0 |
| 과제 | 항공편 지연 이진 분류 |
| 타겟 | `DelayCategory` → 이진화 (0: 정시, 1: 지연) |

---

### 모델 성능 (Test 기준)

**테스트 데이터**: `data/processed/rev_03/flight_delay_test_clean.csv`

#### 전체 지표

| 지표 | 값 |
|------|-----|
| ROC-AUC | 0.6844 |
| Average Precision | 0.5176 |
| 최적 임계값 | 0.52 |
| F1-Score (임계값 0.52) | 0.5373 |

#### 클래스별 성능 (threshold=0.52)

| 클래스 | Precision | Recall | F1-Score |
|-------|-----------|--------|----------|
| 정시(0) | 0.81 | 0.48 | 0.61 |
| 지연(1) | 0.42 | 0.76 | 0.54 |

> 지연 Recall 0.76으로 트리 모델 대비 높음. 단, ROC-AUC(0.6844)와 지연 Precision(0.42)은 낮아 오경보 다수 발생.

---

### 아키텍처 — 2단계(Two-Stage) 구조

1단계에서 정적 특성을 인코딩하고, 2단계에서 그 출력(static_repr)과 동적 특성을 concat하여 함께 처리한다.

```
[1단계 — Static Branch]
  입력: 정적 수치형 12개 + 범주형 임베딩 4종 (임베딩 합계 48-dim → 총 60-dim)
  Embedding: Marketing_Airline_Network(vocab→8), Operating_Airline(vocab→8),
             Origin(vocab→16), Dest(vocab→16)
  FC [60→256→128→64], 마지막 레이어 제외 BatchNorm + ReLU + Dropout(0.3)
  → static_repr (64-dim)

[2단계 — Dynamic Stage]
  입력: Concat(static_repr(64), 동적 특성 22개) → 86-dim
  FC [86→256→128→64], 마지막 레이어 제외 BatchNorm + ReLU + Dropout(0.3)
  → 64-dim
  Linear(64 → 1) → 지연 logit  (예측 시 외부에서 sigmoid 적용)
```

---

### 학습 설정 (Hyperparameters)

| 파라미터 | 값 |
|---------|-----|
| 손실 함수 | BCEWithLogitsLoss |
| pos_weight | (n_neg / n_pos) × 1.5 |
| 옵티마이저 | AdamW |
| 학습률 | 1e-3 |
| weight_decay | 1e-4 |
| 배치 크기 | 2,048 |
| 최대 Epochs | 300 |
| Early Stopping | patience=10 (Val AUC-ROC 기준) |
| LR Scheduler | ReduceLROnPlateau (mode="max", patience=3) |
| random_state | 42 |

---

### 입력 데이터 스펙

#### 정적 특성 (17개) — 비행 출발 전 확정

| 유형 | 특성 수 | 특성명 |
|------|--------|--------|
| 수치형 | 12 | Month, DayofMonth, DayOfWeek, is_weekend, month_sin, month_cos, CRSDep_sin, CRSDep_cos, CRSArr_sin, CRSArr_cos, CRSElapsedTime, is_codeshare |
| 범주형 | 4 | Marketing_Airline_Network, Operating_Airline, Origin, Dest |


#### 동적 특성 (22개) — 운항 당일 실시간 변화

| 유형 | 특성 수 | 특성명 |
|------|--------|--------|
| 기상 (출발지/도착지) | 16 | origin/dest: precipitation_mm, snowfall_cm, windspeed_max_kmh, windgusts_max_kmh, temp_max_c, cloudcover_mean_pct, has_precip, has_snow |
| 운영 지연 지표 | 4 | origin_taxiout_mean, origin_hour_taxiout_mean, dest_taxiin_mean, dest_hour_taxiin_mean |
| 스케줄 편차 | 2 | expected_elapsed_over_schedule, expected_elapsed_hour_over_schedule |

#### 전처리 방법

| 특성 유형 | 전처리 방법 |
|---------|-----------|
| 범주형 4종 | LabelEncoder (어휘: train+test 합집합으로 fit) |
| 수치형 34종 (정적 12 + 동적 22) | StandardScaler (train에만 fit, test에 transform) |
| 클래스 불균형 | pos_weight = (n_neg / n_pos) × 1.5 (BCEWithLogitsLoss) |


---

### 모델 한계점

| 항목 | 내용 |
|------|------|
| ROC-AUC | 0.6844 — 트리 모델(XGBoost 0.8437) 대비 낮음 |
| 지연 Precision | 0.42 — 오경보(FP) 다수 발생 |
| 임계값 | 기본 0.5 대신 0.52 적용 시 F1 최적화 |

> FCNN rev_03 (Focal Loss + CosineAnnealingWarmRestarts + 확장 임베딩) 학습 시 성능 개선 기대


---

### 프로젝트 한계점 및 개선안

| 항목 | 내용 |
|------|------|
| 모델 신뢰성 | 모델 학습 시에는 실제 날씨 데이터를 사용하였으나 예측 시 예보 데이터 활용 |
| 연동성 | 실제 공항 데이터 API와 연동한게 아닌, 임의의 데이터로 실험 진행 |
| 데이터 부족 | Data Drift 실험에 사용할 분포가 다를 정도의 충분한 미래 데이터 미확보 | 