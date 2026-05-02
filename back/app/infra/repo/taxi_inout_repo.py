def find_taxi_inout_by_airport(conn, airport_code: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT operation_hour, taxiin_mean, taxiout_mean
            FROM taxi_inout
            WHERE airport_code=%s
            """,
            (airport_code,)
        )
        return cur.fetchall()