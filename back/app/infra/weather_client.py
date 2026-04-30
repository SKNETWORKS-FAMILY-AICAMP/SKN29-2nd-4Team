from datetime import date, timedelta
import pandas as pd
import requests
from back.app.infra.constants import DAILY_VARIABLES, COLUMN_MAP, STATE_COORDS  # constants.py에서 불러오기

def fetch_weather(state: str, date_str: str) -> dict:
    """
    주 이름과 날짜를 받아서 Open-Meteo에서 날씨를 가져옵니다.
    """
    coords = STATE_COORDS.get(state.lower())

    if coords is None:
        raise ValueError(f"'{state}' 는 등록되지 않은 주 이름입니다")

    lat, lon = coords

    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date_str,
        "end_date": date_str,
        "daily": ",".join(DAILY_VARIABLES),
        "timezone": "America/Chicago",
    }

    response = requests.get(url, params=params)
    response.raise_for_status()

    daily = response.json()["daily"]
    return {var: daily[var][0] for var in DAILY_VARIABLES if var in daily}


def _rename_columns(raw: dict, prefix: str) -> dict:
    """
    Open-Meteo 항목명을 우리 컬럼명으로 변환합니다.
    """
    renamed = {}

    for api_key, col_template in COLUMN_MAP.items():
        col_name = col_template.format(prefix=prefix)
        renamed[col_name] = raw.get(api_key)

    renamed[f"{prefix}_has_precip"] = (raw.get("precipitation_sum") or 0) > 0
    renamed[f"{prefix}_has_snow"]   = (raw.get("snowfall_sum") or 0) > 0

    return renamed


def get_flight_weather(origin_state: str, dest_state: str, date_str: str) -> dict:
    """
    출발지/도착지 날씨를 합쳐서 반환합니다.
    """
    origin_raw = fetch_weather(origin_state, date_str)
    dest_raw   = fetch_weather(dest_state,   date_str)

    origin_data = _rename_columns(origin_raw, prefix="origin")
    dest_data   = _rename_columns(dest_raw,   prefix="dest")

    return {"date": date_str, **origin_data, **dest_data}


def fetch_forecast(origin_state: str, dest_state: str) -> pd.DataFrame:
    """
    오늘 기준 7일 예보 데이터를 가져와서 DataFrame으로 반환
    과거 데이터와 다르게 예보는 api.open_meteo.com을 사용
    """

    today = date.today()
    end_date = today + timedelta(days=7) # 날짜 간격 ( 7일 )

    def fetch_forecast_raw(state: str) -> dict:
        coords = STATE_COORDS.get(state.lower())

        if coords is None:
            raise ValueError(f"'{state}'는 등록되지 않은 주 이름입니다")
        
        lat, lon = coords

        url = "https://api.open-meteo.com/v1/forecast"  # 예보용 엔드포인트
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": today.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "daily": ",".join(DAILY_VARIABLES),
            "timezone": "America/Chicago",
        }

        response = requests.get(url, params=params)
        response.raise_for_status() # 200 외 응답이면 즉시 에러 발생 (404, 500 등)

        return response.json()["daily"] # 날짜별 리스트로 옴
    
    # 각각 예보 데이터 가져오기
    origin_raw = fetch_forecast_raw(origin_state)
    dest_raw = fetch_forecast_raw(dest_state)

    dates = origin_raw["time"]

    rows = []
    for i, d in enumerate(dates):
        row = {"date": d}

        # origin column
        for var in DAILY_VARIABLES:
            col = COLUMN_MAP[var].format(prefix="origin")
            row[col] = origin_raw[var][i]

        # dest column
        for var in DAILY_VARIABLES:
            col = COLUMN_MAP[var].format(prefix="dest")
            row[col] = dest_raw[var][i]

        # 파생 컬럼
        row["origin_has_precip"] = (origin_raw["precipitation_sum"][i] or 0) > 0
        row["origin_has_snow"] = (origin_raw["snowfall_sum"][i] or 0) > 0
        row["dest_has_precip"] = (dest_raw["precipitation_sum"][i] or 0) > 0
        row["dest_has_snow"] = (dest_raw["snowfall_sum"][i] or 0) > 0

        rows.append(row)

    return pd.DataFrame(rows)