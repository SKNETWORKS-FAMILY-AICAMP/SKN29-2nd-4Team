from datetime import date, timedelta
import pandas as pd
import requests

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
    end_date = today + timedelta(days=14) # 날짜 간격 14

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


# === Const ===

# Open-Meteo API에 요청할 날씨 항목 목록
DAILY_VARIABLES = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "snowfall_sum",
    "windspeed_10m_max",
    "windgusts_10m_max",
    "cloudcover_mean",
]

# Open-Meteo 항목명 → 우리 컬럼명 매핑
COLUMN_MAP = {
    "temperature_2m_max":  "{prefix}_temp_max_c",
    "temperature_2m_min":  "{prefix}_temp_min_c",
    "temperature_2m_mean": "{prefix}_temp_mean_c",
    "precipitation_sum":   "{prefix}_precipitation_mm",
    "snowfall_sum":        "{prefix}_snowfall_cm",
    "windspeed_10m_max":   "{prefix}_windspeed_max_kmh",
    "windgusts_10m_max":   "{prefix}_windgusts_max_kmh",
    "cloudcover_mean":     "{prefix}_cloudcover_mean_pct",
}

# 미국 주 이름 → 주도 좌표
STATE_COORDS = {
    "alabama":        (32.3617, -86.2792),
    "alaska":         (58.3005, -134.4197),
    "arizona":        (33.4484, -112.0740),
    "arkansas":       (34.7465, -92.2896),
    "california":     (38.5767, -121.4934),
    "colorado":       (39.7392, -104.9903),
    "connecticut":    (41.7658, -72.6851),
    "delaware":       (39.1582, -75.5244),
    "florida":        (30.4383, -84.2807),
    "georgia":        (33.7490, -84.3880),
    "hawaii":         (21.3070, -157.8584),
    "idaho":          (43.6150, -116.2023),
    "illinois":       (39.7983, -89.6544),
    "indiana":        (39.7684, -86.1581),
    "iowa":           (41.5908, -93.6208),
    "kansas":         (39.0473, -95.6752),
    "kentucky":       (38.1867, -84.8753),
    "louisiana":      (30.4515, -91.1871),
    "maine":          (44.3106, -69.7795),
    "maryland":       (38.9784, -76.4922),
    "massachusetts":  (42.3601, -71.0589),
    "michigan":       (42.7325, -84.5555),
    "minnesota":      (44.9537, -93.0900),
    "mississippi":    (32.2988, -90.1848),
    "missouri":       (38.5767, -92.1735),
    "montana":        (46.5958, -112.0270),
    "nebraska":       (40.8136, -96.7026),
    "nevada":         (39.1638, -119.7674),
    "new hampshire":  (43.2081, -71.5376),
    "new jersey":     (40.2206, -74.7597),
    "new mexico":     (35.6672, -105.9644),
    "new york":       (42.6526, -73.7562),
    "north carolina": (35.7796, -78.6382),
    "north dakota":   (46.8083, -100.7837),
    "ohio":           (39.9612, -82.9988),
    "oklahoma":       (35.4676, -97.5164),
    "oregon":         (44.9429, -123.0351),
    "pennsylvania":   (40.2732, -76.8867),
    "rhode island":   (41.8240, -71.4128),
    "south carolina": (34.0007, -81.0348),
    "south dakota":   (44.3668, -100.3538),
    "tennessee":      (36.1627, -86.7816),
    "texas":          (30.2672, -97.7431),
    "utah":           (40.7608, -111.8910),
    "vermont":        (44.2601, -72.5754),
    "virginia":       (37.5407, -77.4360),
    "washington":     (47.0379, -122.9007),
    "west virginia":  (38.3498, -81.6326),
    "wisconsin":      (43.0731, -89.4012),
    "wyoming":        (41.1400, -104.8202),
}