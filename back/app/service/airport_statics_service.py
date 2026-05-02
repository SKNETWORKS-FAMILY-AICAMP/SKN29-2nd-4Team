from statistics import mean

from back.app.infra.airtime_repo import find_airtime_by_route
from back.app.infra.taxi_inout_repo import find_taxi_inout_by_airport


def get_airtime(conn, route: str, hour: int):
    rows = find_airtime_by_route(conn, route)
    if not rows:
        return None, None

    airtime_mean = mean(r[1] for r in rows if r[1] is not None)
    airtime_actual = next(
        (r[1] for r in rows if r[0] == hour),
        None
    )

    # fallback
    airtime_actual = airtime_actual or airtime_mean
    return airtime_mean, airtime_actual


def get_taxiout(conn, airport_code: str, hour: int):
    rows = find_taxi_inout_by_airport(conn, airport_code)
    if not rows:
        return None, None

    taxiout_mean = mean(r[2] for r in rows if r[2] is not None)
    taxiout_actual = next(
        (r[2] for r in rows if r[0] == hour),
        None
    )

    taxiout_actual = taxiout_actual or taxiout_mean
    return taxiout_mean, taxiout_actual


def get_taxiin(conn, airport_code: str, hour: int):
    rows = find_taxi_inout_by_airport(conn, airport_code)
    if not rows:
        return None, None

    taxiin_mean = mean(r[1] for r in rows if r[1] is not None)
    taxiin_actual = next(
        (r[1] for r in rows if r[0] == hour),
        None
    )

    taxiin_actual = taxiin_actual or taxiin_mean
    return taxiin_mean, taxiin_actual