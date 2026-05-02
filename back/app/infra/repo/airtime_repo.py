def find_airtime_by_route(conn, route: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT crs_dep_hour, airtime_mean
            FROM airtime
            WHERE route=%s
            """,
            (route,)
        )
        return cur.fetchall()