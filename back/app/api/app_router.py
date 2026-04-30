from fastapi import APIRouter
from pydantic import BaseModel, RootModel
from typing import List, Dict, Any
import random


router = APIRouter(prefix="/api")


class Reservation(RootModel[Dict[str, Any]]):
    pass

class ReservationItem(BaseModel):
    rank: int
    delay: float
    reservation: Reservation


class ReservationRankRequest(BaseModel):
    depart: str
    arrive: str
    # 인풋 추가

class ReservationRankResponse(BaseModel):
    items: List[ReservationItem]

@router.post("/reservation-rank", response_model=ReservationRankResponse)
def reservation_rank(request: ReservationRankRequest):
    """
    request => pred_batch
    => model.predict()
    => ranked items
    """
    # 샘플 응답 생성
    items = []
    for i in range(10):
        delay = round(random.uniform(1, 10), 2)
        items.append({
            "rank": i + 1,
            "delay": delay,
            "reservation": {
                "name": f"sample-reservation-{i+1}"
            }
        })

    items = sorted(items, key=lambda x: x["delay"])
    for idx, item in enumerate(items):
        item["rank"] = idx + 1

    return {"items": items}
    

@router.post("/check-my-reservation", response_model=ReservationItem)
def check_my_reservation(myreservation: Reservation):
    """
    reservation => pred_row
    => model.predict()
    => result
    """
    delay = round(random.uniform(1, 10), 2)
    return {
        "rank": 1,
        "delay": delay,
        "reservation": {
            "name": f"sample-reservation-{1}"
        }
    }


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