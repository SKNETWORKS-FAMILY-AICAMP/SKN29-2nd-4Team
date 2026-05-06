# 📄 산출물 2: 인공지능 학습 결과서

## 1. 모델링 전략

### 1-1. 과제 정의

| 항목 | 내용 |
|------|------|
| 과제 | 항공편 지연 이진 분류 |
| 타겟 변수 | `DelayCategory` → 이진화 (`DelayCategory > 0` → 지연) |
| 클래스 정의 | 0: 정시 도착, 1: 지연 도착 |
| 테스트 데이터 | `data/processed/rev_03/flight_delay_test_clean.csv` |
| 테스트 샘플 수 | 929,965건 (정시 626,834건 67.4% / 지연 303,131건 32.6%) |

---

### 1-2. 평가 지표 선정

| 지표 | 선정 이유 |
|------|----------|
| ROC-AUC | 임계값에 독립적인 전반적 분류 성능 — **최우선 선정 지표** |
| Average Precision | 지연 클래스의 Precision-Recall 균형 평가 |
| Recall (지연 클래스) | 실제 지연을 놓치는 것이 운영 손실 직결 — 보조 지표 |
| F1-Score (지연 클래스) | Precision-Recall 균형 |
| Accuracy | 참고용 (클래스 불균형 데이터에서 단독 사용 지양) |

> ⚠️ False Negative(지연인데 정시로 예측) → 승객 불편 및 운영 손실 직결  
> → **ROC-AUC를 최우선으로, Recall(지연 클래스)을 보조 지표로 설정**

---

### 1-3. 후보 모델 선정

| 모델 | 유형 | 선정 근거 |
|------|------|----------|
| XGBoost | 트리 기반 부스팅 | 분류 성능 우수, 범주형 변수 네이티브 지원, 업계 표준 |
| LightGBM | 트리 기반 부스팅 | 빠른 학습 속도, 대용량 데이터 효율적 처리 |
| RandomForest | 트리 기반 배깅 | 과적합 저항성, 안정적 기준 모델, 특성 중요도 제공 |
| Stacking | 메타 앙상블 | 3개 베이스 모델 조합으로 일반화 성능 향상 기대 |
| FCNN | 딥러닝 | 정적 인코딩 후 동적 특성과 결합하는 2단계 구조, 비선형 패턴 포착 |

---

### 1-4. 실험 계획

- 학습/테스트 데이터: `data/processed/rev_03/` (전체 데이터 사용)
- 트리 모델 3종에 **Optuna HPO (70 trials)** 적용 — 최적화 목표: ROC-AUC
- Stacking: 학습 데이터 **70/30 분할** (베이스 학습 / 블렌딩 세트)
- FCNN: Early Stopping (patience=10) 적용
- 클래스 불균형 대응: 트리 모델 — 클래스 가중치 √(n / (2 × count[c])) / FCNN — pos_weight = (n_neg / n_pos) × 1.5
- 최종 모델 선정 기준: **Test ROC-AUC 최고값**

---

## 2. 머신러닝 모델 학습 결과

### 2-1. XGBoost

#### 하이퍼파라미터 탐색 (Optuna HPO, 70 trials)

| 파라미터 | 탐색 범위 | 유형 |
|---------|---------|------|
| n_estimators | 100 ~ 1,000 | int |
| max_depth | 3 ~ 10 | int |
| learning_rate | 0.01 ~ 0.30 | float (log scale) |
| subsample | 0.6 ~ 1.0 | float |
| colsample_bytree | 0.6 ~ 1.0 | float |
| min_child_weight | 1 ~ 10 | int |
| reg_lambda | 0.001 ~ 10.0 | float (log scale) |

#### 고정 설정

| 파라미터 | 값 |
|---------|-----|
| objective | binary:logistic |
| eval_metric | logloss |
| tree_method | hist |
| enable_categorical | True |
| early_stopping_rounds | 50 |
| random_state | 42 |
| 클래스 가중치 | √(n / (2 × count[c])) |
| 범주형 인코딩 | pandas CategoricalDtype (어휘: train+test 합집합) |

#### 성능 결과 (Test 기준)

| 지표 | 값 |
|------|-----|
| **ROC-AUC** | **0.8437** |
| Average Precision | 0.5356 |
| Accuracy | 0.70 |

#### 분류 보고서 (Test)

|  | Precision | Recall | F1-Score | Support |
|--|-----------|--------|----------|---------|
| 정시(0) | 0.74 | 0.85 | 0.79 | 626,834 |
| 지연(1) | 0.55 | 0.39 | 0.46 | 303,131 |
| macro avg | 0.65 | 0.62 | 0.63 | 929,965 |
| weighted avg | 0.68 | 0.70 | 0.68 | 929,965 |

#### 혼동 행렬

|  | 예측: 정시(0) | 예측: 지연(1) |
|--|-------------|-------------|
| **실제: 정시(0)** | 530,361 (TN) | 96,473 (FP) |
| **실제: 지연(1)** | 183,728 (FN) | 119,403 (TP) |

- **TP** (지연 → 지연): 119,403건 — 정확히 탐지된 지연 항공편
- **FN** (지연 → 정시): 183,728건 — 놓친 지연 항공편 (운영 손실)
- **FP** (정시 → 지연): 96,473건 — 불필요한 경보 발생
- **TN** (정시 → 정시): 530,361건

---

### 2-2. LightGBM

#### 하이퍼파라미터 탐색 (Optuna HPO, 70 trials)

| 파라미터 | 탐색 범위 | 유형 |
|---------|---------|------|
| n_estimators | 100 ~ 1,000 | int |
| num_leaves | 20 ~ 150 | int |
| learning_rate | 0.01 ~ 0.30 | float (log scale) |
| subsample | 0.6 ~ 1.0 | float |
| colsample_bytree | 0.6 ~ 1.0 | float |
| min_child_samples | 10 ~ 50 | int |
| reg_lambda | 0.001 ~ 10.0 | float (log scale) |

#### 고정 설정

| 파라미터 | 값 |
|---------|-----|
| objective | binary |
| early_stopping patience | 50 |
| random_state | 42 |
| verbose | -1 |
| 클래스 가중치 | √(n / (2 × count[c])) |
| 범주형 인코딩 | pandas CategoricalDtype |

#### 성능 결과 (Test 기준)

| 지표 | 값 |
|------|-----|
| **ROC-AUC** | **0.8376** |
| Average Precision | 0.5244 |
| Accuracy | 0.69 |

#### 분류 보고서 (Test)

|  | Precision | Recall | F1-Score | Support |
|--|-----------|--------|----------|---------|
| 정시(0) | 0.74 | 0.84 | 0.79 | 626,834 |
| 지연(1) | 0.54 | 0.39 | 0.46 | 303,131 |
| macro avg | 0.64 | 0.62 | 0.62 | 929,965 |
| weighted avg | 0.68 | 0.69 | 0.68 | 929,965 |

#### 혼동 행렬

|  | 예측: 정시(0) | 예측: 지연(1) |
|--|-------------|-------------|
| **실제: 정시(0)** | 525,651 (TN) | 101,183 (FP) |
| **실제: 지연(1)** | 183,664 (FN) | 119,467 (TP) |

---

### 2-3. RandomForest

#### 하이퍼파라미터 탐색 (Optuna HPO, 70 trials)

| 파라미터 | 탐색 범위 | 유형 |
|---------|---------|------|
| n_estimators | 50 ~ 300 | int |
| max_depth | 5 ~ 20 | int |
| min_samples_split | 2 ~ 20 | int |
| min_samples_leaf | 1 ~ 10 | int |
| max_features | sqrt / log2 / 0.5 | categorical |
| class_weight | balanced / balanced_subsample | categorical |

#### 고정 설정

| 파라미터 | 값 |
|---------|-----|
| random_state | 42 |
| 범주형 인코딩 | TargetEncoder (smooth="auto", target_type="binary") |
| 인코더 fit 기준 | 학습 데이터에만 fit (데이터 누수 방지) |

#### 성능 결과 (Test 기준)

| 지표 | 값 |
|------|-----|
| **ROC-AUC** | **0.8278** |
| Average Precision | 0.5135 |
| Accuracy | 0.67 |

#### 분류 보고서 (Test)

|  | Precision | Recall | F1-Score | Support |
|--|-----------|--------|----------|---------|
| 정시(0) | 0.76 | 0.75 | 0.75 | 626,834 |
| 지연(1) | 0.49 | 0.50 | 0.49 | 303,131 |
| macro avg | 0.62 | 0.62 | 0.62 | 929,965 |
| weighted avg | 0.67 | 0.67 | 0.67 | 929,965 |

#### 혼동 행렬

|  | 예측: 정시(0) | 예측: 지연(1) |
|--|-------------|-------------|
| **실제: 정시(0)** | 469,988 (TN) | 156,846 (FP) |
| **실제: 지연(1)** | 152,233 (FN) | 150,898 (TP) |

**특이사항**: 지연 Recall 0.50으로 트리 모델 중 최고 — 미탐지 최소화 우선 시 대안

---

### 2-4. Stacking (메타 앙상블)

#### 아키텍처

```
베이스 레이어 (학습 데이터 70% 사용):
  ├── XGBoost  (CategoricalDtype 인코딩)
  ├── LightGBM (CategoricalDtype 인코딩)
  └── RandomForest (TargetEncoder)

메타 레이어 (블렌딩 세트 30% 사용):
  └── LogisticRegression
      입력: [P_xgb, P_lgbm, P_rf] → 3차원 확률 벡터
      C=1.0, max_iter=1000, random_state=42
```

#### 성능 결과 (Test 기준)

| 지표 | 값 |
|------|-----|
| **ROC-AUC** | **0.8412** |
| Average Precision | 0.5326 |
| Accuracy | **0.71** |

#### 분류 보고서 (Test)

|  | Precision | Recall | F1-Score | Support |
|--|-----------|--------|----------|---------|
| 정시(0) | 0.72 | 0.92 | 0.81 | 626,834 |
| 지연(1) | **0.61** | 0.27 | 0.37 | 303,131 |
| macro avg | 0.67 | 0.59 | 0.59 | 929,965 |
| weighted avg | 0.69 | 0.71 | 0.67 | 929,965 |

#### 혼동 행렬

|  | 예측: 정시(0) | 예측: 지연(1) |
|--|-------------|-------------|
| **실제: 정시(0)** | 574,238 (TN) | 52,596 (FP) |
| **실제: 지연(1)** | 221,220 (FN) | 81,911 (TP) |

**특이사항**: 지연 Precision 0.61로 전체 모델 중 최고 — 오경보 최소화 우선 시 대안. 단, 지연 Recall 0.27로 전체 최저

---

## 3. 딥러닝 모델 학습 결과 (FCNN)

### 3-1. 모델 구조 — 2단계(Two-Stage) FCNN 아키텍처

```
[1단계 — Static Branch]
  입력: 정적 수치형 12개 + 범주형 임베딩 4종
        임베딩 합계 48-dim (8+8+16+16) + 수치형 12-dim → 총 60-dim

  임베딩 레이어 (범주형 4종)
    Marketing_Airline_Network → Embedding(vocab, 8)
    Operating_Airline         → Embedding(vocab, 8)
    Origin                    → Embedding(vocab, 16)
    Dest                      → Embedding(vocab, 16)

  Linear(60 → 256) → BatchNorm → ReLU → Dropout(0.3)
  Linear(256 → 128) → BatchNorm → ReLU → Dropout(0.3)
  Linear(128 → 64)
        │
        ▼ static_repr (64-dim)

[2단계 — Dynamic Stage]
  입력: Concat(static_repr(64), 동적 특성 22개) → 86-dim
        동적 특성: 기상 16 + 운영 지표 4 + 스케줄 편차 2, StandardScaler 적용

  Linear(86 → 256) → BatchNorm → ReLU → Dropout(0.3)
  Linear(256 → 128) → BatchNorm → ReLU → Dropout(0.3)
  Linear(128 → 64)
        │
  Linear(64 → 1) → 지연 logit
  ※ Sigmoid 없음 — BCEWithLogitsLoss 학습, 예측 시 외부에서 sigmoid 적용
```

### 3-2. 학습 설정

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

### 3-3. 성능 결과 (Test 기준)

| 지표 | 값 |
|------|-----|
| **ROC-AUC** | **0.6844** |
| Average Precision | 0.5176 |
| 최적 임계값 | 0.52 |
| F1-Score (임계값 0.52) | 0.5373 |

#### 분류 보고서 (Test, threshold=0.52)

|  | Precision | Recall | F1-Score |
|--|-----------|--------|----------|
| 정시(0) | 0.81 | 0.48 | 0.61 |
| 지연(1) | 0.42 | **0.76** | 0.54 |

**특이사항**:
- 지연 Recall 0.76으로 트리 모델 대비 현저히 높음 (XGBoost: 0.39)
- 그러나 ROC-AUC 0.6844로 트리 모델 대비 낮음 (XGBoost: 0.8437)
- Precision 0.42로 낮아 오경보(FP) 다수 발생
- 지연 탐지 극대화가 필요한 시나리오에서 대안 고려 가능

---

## 4. 모델 종합 비교 및 최적 모델 선정

### 4-1. 전체 모델 성능 비교표 (Test 기준)

| 모델 | ROC-AUC | Avg Precision | Accuracy | 지연 Precision | 지연 Recall | 지연 F1 |
|------|---------|-------------|---------|-------------|-----------|--------|
| **XGBoost** | **0.8437** | **0.5356** | 0.70 | 0.55 | 0.39 | 0.46 |
| Stacking | 0.8412 | 0.5326 | **0.71** | **0.61** | 0.27 | 0.37 |
| LightGBM | 0.8376 | 0.5244 | 0.69 | 0.54 | 0.39 | 0.46 |
| RandomForest | 0.8278 | 0.5135 | 0.67 | 0.49 | 0.50 | 0.49 |
| FCNN | 0.6844 | 0.5176 | — | 0.42 | **0.76** | **0.54** |

### 4-2. 지표별 최고 성능 모델

| 지표 | 최고 모델 | 값 |
|------|---------|-----|
| ROC-AUC ⭐ (최우선) | **XGBoost** | 0.8437 |
| Average Precision | XGBoost | 0.5356 |
| Accuracy | Stacking | 0.71 |
| 지연 Precision | Stacking | 0.61 |
| 지연 Recall | FCNN | 0.76 |
| 지연 F1-Score | FCNN | 0.54 |

### 4-3. 보수적 임계값 적용 변형 모델 (_FINAL)

임계값을 높게 설정하여 정시 정확도를 극대화한 변형 모델. 지연 탐지 능력 대폭 저하.

| 모델 | ROC-AUC | Avg Precision | 지연 Recall | 비고 |
|------|---------|-------------|-----------|------|
| LGBM_FINAL | 0.8217 | 0.4223 | 0.05 | 보수적 임계값 — 정시 Recall 0.98 |
| XGBOOST_FINAL | 0.8234 | 0.4002 | 0.02 | 보수적 임계값 — 정시 Recall 0.99 |
| RF_FINAL | 0.8159 | 0.3504 | 0.00 | 사실상 지연 미탐지 — 정시 Recall 1.00 |

---

### 4-4. 최적 모델 선정

**선정 모델: XGBoost**

**선정 근거**:
1. ROC-AUC **0.8437** — 트리 기반 모델 중 최고 성능
2. Average Precision **0.5356** — 전체 모델 중 최고
3. XGBoost/LightGBM 지연 F1 동일(0.46)이나 XGBoost Accuracy 우위 (0.70 vs 0.69)
4. 단일 모델로 배포 및 유지보수 간소화 (Stacking 대비)
5. 범주형 변수 네이티브 지원으로 전처리 파이프라인 단순화

**트레이드오프 분석**:

| 시나리오 | 권장 모델 | 근거 |
|---------|---------|------|
| 기본 (AUC 최우선) | **XGBoost** | ROC-AUC 0.8437 최고 |
| 오경보 최소화 | Stacking | 지연 Precision 0.61 최고 |
| 미탐지 최소화 | RandomForest | 지연 Recall 0.50 최고 (트리 중) |
| Recall 극대화 | FCNN | 지연 Recall 0.76 (ROC-AUC 저하 감수) |

### 4-5. ROC-AUC 성능 향상 요인

초기 다중 분류 실험(4클래스, F1 Macro 0.27) 대비 XGBoost ROC-AUC 0.8437 달성의 기여 요인.

| 요인 | 변경 내용 | 효과 |
|------|---------|------|
| 이진 분류 전환 | 4클래스 → 2클래스 (`DelayCategory > 0`) | 결정 경계 단순화, 지표 해석 일관성 확보 |
| 전체 데이터 학습 | minibatch 일부 → rev_03 전체 비행 이력 | 항공사·노선·기상 패턴 다양성 확보 |
| Optuna HPO | 70 trials, ROC-AUC 직접 최적화 | 과적합 방지(reg_lambda, subsample) + 트리 복잡도 최적화 |
| 클래스 가중치 | √(n / (2 × count[c])) 적용 | 지연 클래스(33%) 학습 신호 강화 |

---

## 5. 모델 해석

### 5-1. 입력 특성 구성 — 정적/동적 분리 설계

> - **정적 (Static)**: 비행 출발 전 확정 — 스케줄·노선·항공사 정보, 당일 변화 없음
> - **동적 (Dynamic)**: 운항 당일 수집 — 기상 조건·운영 지표

#### 정적 특성 (총 16개)

| 유형 | 특성 수 | 특성 목록 |
|------|--------|---------|
| 수치형 | 12 | Month, DayofMonth, DayOfWeek, is_weekend, month_sin, month_cos, CRSDep_sin, CRSDep_cos, CRSArr_sin, CRSArr_cos, CRSElapsedTime, is_codeshare |
| 범주형 | 4 | Marketing_Airline_Network, Operating_Airline, Origin, Dest |

#### 동적 특성 (총 22개)

| 유형 | 특성 수 | 특성 목록 |
|------|--------|---------|
| 기상 (출발지/도착지) | 16 | origin/dest: precipitation_mm, snowfall_cm, windspeed_max_kmh, windgusts_max_kmh, temp_max_c, cloudcover_mean_pct, has_precip, has_snow |
| 운영 지연 지표 | 4 | origin_taxiout_mean, origin_hour_taxiout_mean, dest_taxiin_mean, dest_hour_taxiin_mean |
| 스케줄 편차 | 2 | expected_elapsed_over_schedule, expected_elapsed_hour_over_schedule |

#### 모델별 정적/동적 처리 방식

| 모델 | 처리 방식 |
|------|---------|
| **XGBoost / LightGBM / RF / Stacking** | 정적 + 동적 특성을 **단일 입력 벡터로 결합**하여 트리에 입력 (구조적 분리 없음, 범주형은 별도 인코딩) | 
| **FCNN** | **2단계 구조**: 1단계에서 정적 특성을 인코딩(static_repr) → 2단계에서 static_repr과 동적 특성을 concat하여 함께 처리 → 최종 logit 출력 |

**제거된 다중공선성 특성 (VIF 기반, 12개)**:  
`expected_elapsed_mean`, `expected_elapsed_hour_mean`, `schedule_buffer_hour`, `schedule_buffer`, `route_hour_airtime_mean`, `route_airtime_mean`, `origin_temp_mean_c`, `origin_temp_min_c`, `dest_temp_mean_c`, `dest_temp_min_c`, `Distance`, `FlightDate`

### 5-2. 클래스 불균형 대응 전략

- **데이터 비율**: 정시 67.4% / 지연 32.6% (약 2:1)
- **적용 전략**: 클래스 가중치 — √(n_samples / (n_classes × count[c]))
- **효과**: 지연 클래스 예측 감도 향상, 단순 majority class 예측 방지

### 5-3. 데이터 드리프트 모니터링

- **감지 기준**: ROC-AUC < **0.80** → 재학습 자동 트리거

**증분 학습 전략**:

| 모델 | 증분 학습 방식 |
|------|-------------|
| XGBoost | `xgb_model=model.get_booster()` 로 이어 학습 |
| LightGBM | `init_model=model` 로 이어 학습 |
| RandomForest | `warm_start=True` + 트리 50개 추가 |

> 증분 학습 후에도 ROC-AUC < 0.80이면 저장하지 않고 전체 재학습(`run_full.py`) 권고
