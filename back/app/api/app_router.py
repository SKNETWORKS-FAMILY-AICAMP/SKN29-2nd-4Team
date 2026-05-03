from fastapi import APIRouter, Depends
from pydantic import BaseModel, RootModel
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from back.app.service.pred_input_service import single_input, multi_input
from back.app.service.airport_statics_service import get_mean_triptime
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

@router.post("/reservation-rank", response_model=ReservationRankResponse)
def reservation_rank(request: ReservationRankRequest, conn=Depends(get_conn)):
    start_datetimes, end_datetimes = _generate_time_candidates(conn, request)
    model_input = multi_input(request.depart, request.arrive, start_datetimes, end_datetimes, request.prefered_airlines, conn)
    # model_service.predict(model_name, model_input)
    print(model_input)
    

@router.post("/check-my-reservation", response_model=ReservationItem)
def check_my_reservation(myreservation: Reservation, conn=Depends(get_conn)):
    r = myreservation
    model_input = single_input(conn, r.depart, r.arrive, r.depart_dt, r.arrive_dt, r.airline)
    # model_service.predict(model_name, model_input)
    print(model_input)
    


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