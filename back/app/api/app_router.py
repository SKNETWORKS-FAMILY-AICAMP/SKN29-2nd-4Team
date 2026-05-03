from fastapi import APIRouter, Depends
from pydantic import BaseModel, RootModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random
import numpy as np
import pandas as pd

from back.app.service.pred_input_service import single_input, multi_input
from back.app.service.airport_statics_service import get_mean_triptime
from back.app.service.model_service import predict
from back.app.infra.db import get_conn

router = APIRouter(prefix="/api")


class Reservation(BaseModel):
    depart: str
    arrive: str
    depart_dt: datetime
    arrive_dt: datetime
    airline: str

class ReservationItem(BaseModel):
    rank: int
    delay: float
    reservation: Reservation


class ReservationRankRequest(BaseModel):
    depart: str
    arrive: str
    prefered_depart_time: Optional[int] = None
    prefered_arrive_time: Optional[int] = None
    prefered_airlines: List[str] = ['AA', 'DL', 'UA', 'WN', 'B6']

class ReservationRankResponse(BaseModel):
    items: List[ReservationItem]

class Sample(BaseModel):
    status: str = "ok"
    message: str = "잘 받았습니다~"

TOP_K = 5

@router.post("/reservation-rank", response_model=ReservationRankResponse)
def reservation_rank(request: ReservationRankRequest, conn=Depends(get_conn)):
    start_datetimes, end_datetimes = _generate_time_candidates(conn, request)
    model_input = multi_input(conn, request.depart, request.arrive, start_datetimes, end_datetimes, request.prefered_airlines)
    proba = predict(model_input) # list of 지연확률
    top_indices = np.argsort(proba)[:TOP_K] # 오름차순 top_k 인덱스 번호

    cnt = 1
    items = []
    for i in top_indices:
        reservation = _to_reservation(model_input.iloc[i])
        rank = cnt
        delay = proba[i]
        items.append(ReservationItem(rank=rank, delay=delay, reservation=reservation))
        cnt += 1

    return ReservationRankResponse(items=items)
    

class Weather(BaseModel):
    airport: str
    weather: str
    temperature: float
    wind: float

class CheckMyReservationResponse(BaseModel):
    delay: str
    proba: float
    weather: Weather

@router.post("/check-my-reservation", response_model=CheckMyReservationResponse)
def check_my_reservation(myreservation: Reservation, conn=Depends(get_conn)):
    r = myreservation
    model_input = single_input(conn, r.depart, r.arrive, r.depart_dt, r.arrive_dt, r.airline)
    proba = predict(model_input)[0] # 지연확률 1개

    delay = _estimate_delay(proba)
    weather = _to_weather(model_input)
    return CheckMyReservationResponse(delay=delay, proba=proba, weather=weather)
    


class OLearnResult(BaseModel):
    model_name: str
    before: Dict[str, Any]
    after: Dict[str, Any]

@router.get(
    "/online-learning/{model_name}/result",
    response_model=OLearnResult
)
def get_olearn_result(model_name: str):
    """
    load model report from db
    return
    """
    return {
        "model_name": "sample_model_20220610",
        "before": {
            "mean-mse": 0.0123,
            "is-outdated": False,
            "message": "아직 모델이 현재 데이터도 잘 예측하고있음"
        },
        "after": {}
    }


def _generate_time_candidates(conn, request):
    now = datetime.now()
    horizon = 7 * 24 # 7일 * 24시간

    # 출발시간 생성
    start_datetimes = []
    for i in range(horizon):
        dt = now + timedelta(hours=i)

        # prefered_depart_time 필터 (ex: 13 → 13시 이후만)
        if request.prefered_depart_time is not None:
            if dt.hour < request.prefered_depart_time:
                continue
        start_datetimes.append(dt)

    if not start_datetimes:
        return [], []

    triptime = get_mean_triptime(conn, request.depart, request.arrive)
    alpha = 30  # 여유 30분 (튜닝 가능)
    total_minutes = triptime + alpha

    # 도착시간 생성
    end_datetimes = [
        dt + timedelta(minutes=total_minutes)
        for dt in start_datetimes
    ]

    if request.prefered_arrive_time is not None:
        filtered_start = []
        filtered_end = []

        for s, e in zip(start_datetimes, end_datetimes):
            if e.hour >= request.prefered_arrive_time:
                filtered_start.append(s)
                filtered_end.append(e)

        start_datetimes = filtered_start
        end_datetimes = filtered_end

    return start_datetimes, end_datetimes


def _to_weather(df) -> Weather:
    if isinstance(df, pd.DataFrame):
        row = df.iloc[0]
    elif isinstance(df, pd.Series):
        row = df

    # ── 값 추출 ──
    temp_mean = row.get("dest_temp_mean_c")
    precip = row["dest_precipitation_mm"]
    snow = row["dest_snowfall_cm"]
    wind = row["dest_windspeed_max_kmh"]
    cloud = row["dest_cloudcover_mean_pct"]

    # ── 날씨 판단 ──
    if snow > 0.5:
        weather = "snowy"
    elif precip > 1.0:
        weather = "rainy"
    elif cloud > 70:
        weather = "cloudy"
    else:
        weather = "sunny"

    return Weather(
        airport=row["Dest"],
        weather=weather,
        temperature=temp_mean,
        wind=wind
    )

def _to_reservation(df) -> Reservation:
    if isinstance(df, pd.DataFrame):
        row = df.iloc[0]
    elif isinstance(df, pd.Series):
        row = df

    return Reservation(
        depart=row['Origin'],
        arrive=row['Dest'],
        depart_dt=row['_start_time'],
        arrive_dt=row['_end_time'],
        airline=row['Operating_Airline']
    )

def _estimate_delay(proba):
    if proba < 0.3:
        return "15분 미만"
    elif proba < 0.7:
        return "15분 이상"
    else:
        return "1시간 이상"