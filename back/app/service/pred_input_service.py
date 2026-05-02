from fastapi import Depends
from datetime import datetime
import pandas as pd
import numpy as np

from back.app.infra.db import get_conn
from back.app.service.airport_statics_service import get_airtime, get_taxiin, get_taxiout, get_airport_coords
from back.app.infra.weather_client import fetch_forecast


INPUT_COLUMNS = ["Month", "DayofMonth", "DayOfWeek", "is_weekend", "Origin", "Dest", "Route", "Operating_Airline", "_start_time", "_end_time"]


def single_input(origin, dest, departure_dt, arrive_dt, airline, conn=Depends(get_conn)):
    return get_input(conn, origin, dest, [departure_dt], [arrive_dt], [airline])

def multi_input(origin, dest, start_datetimes, end_datetimes, airlines, conn=Depends(get_conn)):
    return get_input(conn, origin, dest, start_datetimes, end_datetimes, airlines)


def get_input(conn, start_airport, end_airport, start_datetimes, end_datetimes, airlines):
    rows = make_all_rows(start_airport, end_airport, start_datetimes, end_datetimes, airlines)
    df = pd.DataFrame(rows, columns=INPUT_COLUMNS)
    df = feature_pipeline(conn, df)
    # return model input (피쳐 정렬, 인풋 형식에 맞게 변환)
    return df


def _one_row(start_airport, end_airport, start_datetime, end_datetime, airline):
    _, m, d, shh, smm, _, day = _split_datetime(start_datetime)
    _, _, _, ehh, emm, _, _ = _split_datetime(end_datetime)
    return m, d, day+1, day > 4, start_airport, end_airport, f"{start_airport}_{end_airport}", airline, shh*60+smm, ehh*60+emm

def _split_datetime(dt: datetime):
    return dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second, dt.weekday()

def make_all_rows(start_airport, end_airport, start_datetimes, end_datetimes, airlines):
    rows = []
    for i in range(len(start_datetimes)):
        for airline in airlines:
            rows.append(_one_row(start_airport, end_airport, start_datetimes[i], end_datetimes[i], airline))
    return rows


def feature_pipeline(conn, df):
    processed = df.copy()
    processed["CRSDep_sin"] = np.sin(2 * np.pi * processed["_start_time"] / 1440)
    processed["CRSDep_cos"] = np.cos(2 * np.pi * processed["_start_time"] / 1440)
    processed["CRSArr_sin"] = np.sin(2 * np.pi * processed["_end_time"] / 1440)
    processed["CRSArr_cos"] = np.cos(2 * np.pi * processed["_end_time"] / 1440)

    # 티켓의 예상 소요시간
    processed["CRSElapsedTime"] = processed["_end_time"] - processed["_start_time"]
    processed.loc[processed["CRSElapsedTime"] < 0, "CRSElapsedTime"] += 24 * 60

    route = df["Route"].iloc[0]
    origin = df["Origin"].iloc[0]
    dest = df["Dest"].iloc[0]
    hour = int(df["_start_time"].iat[0] // 60)
    
    airtime_mean, airtime_actual = get_airtime(conn, route, hour)
    taxiout_mean, taxiout_actual = get_taxiout(conn, origin, hour)
    taxiin_mean, taxiin_actual = get_taxiin(conn, dest, hour)

    # 해당 경로, 시간 별 평균 소요시간과의 차이
    expected_elapsed = taxiout_mean + airtime_mean + taxiin_mean
    processed["expected_elapsed_over_schedule"] = expected_elapsed - processed["CRSElapsedTime"]
    expected_elapsed_hour = taxiout_actual + airtime_actual + taxiin_actual
    processed["expected_elapsed_hour_over_schedule"] = expected_elapsed_hour - processed["CRSElapsedTime"]

    # 날씨
    origin_lat_lon = get_airport_coords(conn, origin)
    dest_lat_lon = get_airport_coords(conn, dest)
    processed["_YMD"] = pd.to_datetime({
        "year": pd.Timestamp.today().year,
        "month": processed["Month"],
        "day": processed["DayofMonth"],
    })

    start_date = processed["_YMD"].min().date()
    end_date = processed["_YMD"].max().date()
    weather_df = fetch_forecast(origin_lat_lon, dest_lat_lon, start_date, end_date)
    weather_df["date"] = pd.to_datetime(weather_df["date"])

    processed = processed.merge(
        weather_df,
        left_on="_YMD",
        right_on="date",
        how="left"
    ).drop(columns=["date"])

    # 항공사
    processed["Marketing_Airline_Network"] = processed["Operating_Airline"]
    processed["is_codeshare"] = 0

    return processed