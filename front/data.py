import streamlit as st
from pydantic import BaseModel
from datetime import datetime, date
from typing import Dict, Any

from front.api.app_client import AppClient
from front.api.schema import Reservation, ReservationRankRequest

client = AppClient("http://localhost:8000")


@st.cache_data
def get_airports():
    return client.get_airports()["items"]

@st.cache_data
def get_airlines():
    return client.get_airlines()["items"]


def set_user_reservation(
    depart: str,
    arrive: str,
    dep_dt: datetime,
    arr_dt: datetime,
    airline: str
):
    reservation = Reservation(
        depart=depart,
        arrive=arrive,
        depart_dt=dep_dt,
        arrive_dt=arr_dt,
        airline=airline
    )

    st.session_state.user_reservation = reservation.model_dump()
    
def get_user_reservation() -> Reservation | None:
    data = st.session_state.get("user_reservation")
    if data is None:
        return None
    return Reservation(**data)


def set_check_my_reservation(result):
    pass

def set_user_pref_reservations(depart, arrive, pref_dep_hour, pref_arr_hour, pref_airlines):
    def to_int_or_none(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return None
    dep_hour = to_int_or_none(pref_dep_hour)
    arr_hour = to_int_or_none(pref_arr_hour)
    airlines = pref_airlines if pref_airlines else None

    request = ReservationRankRequest(
        depart=depart,
        arrive=arrive,
        prefered_depart_time=dep_hour,
        prefered_arrive_time=arr_hour,
        prefered_airlines=airlines,
    )

    st.session_state.user_rank_reservation_request = request.model_dump()

def get_user_pref_reservations() -> ReservationRankRequest | None:
    data = st.session_state.get("user_rank_reservation_request")
    if data is None:
        return None
    return Reservation(**data)

def set_rank_reservations_result(result):
    pass