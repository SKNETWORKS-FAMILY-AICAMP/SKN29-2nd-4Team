def find_all_active_airports(conn):
    """
    disabled != 1 인 공항 전체 조회
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT airport_code, airport_name_ko
            FROM airport_info
            WHERE disabled != 1 OR disabled IS NULL
            """
        )
        return cur.fetchall()

    
def find_airport_coords(conn, airport_code: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT LATITUDE, LONGITUDE
            FROM airport_info
            WHERE airport_code=%s
              AND (disabled != 1 OR disabled IS NULL)
            """,
            (airport_code,)
        )
        row = cur.fetchone()
        if not row:
            return None
        return row[0], row[1]
    

def find_airport_by_code(conn, airport_code: str):
    """
    특정 공항 조회 (disabled 제외)
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT airport_code, airport_name_en, airport_name_ko, LATITUDE, LONGITUDE
            FROM airport_info
            WHERE airport_code=%s
              AND (disabled != 1 OR disabled IS NULL)
            """,
            (airport_code,)
        )
        return cur.fetchone()