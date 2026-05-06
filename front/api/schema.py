from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class Reservation(BaseModel):
    depart: str
    arrive: str
    depart_dt: datetime
    arrive_dt: datetime
    airline: str

class ReservationRankRequest(BaseModel):
    depart: str
    arrive: str
    prefered_depart_time: Optional[int] = None
    prefered_arrive_time: Optional[int] = None
    prefered_airlines: List[str] = ['AA', 'DL', 'UA', 'WN', 'B6']