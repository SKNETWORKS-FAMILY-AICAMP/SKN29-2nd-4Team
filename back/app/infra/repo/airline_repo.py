def find_all_airlines(conn):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT code, name
            FROM airline
            ORDER BY code
        """)
        return cur.fetchall()