import os
import pandas as pd
import pymysql
from dotenv import load_dotenv

"""
route_hour_airtime_stats.csv는 80000 row라서
insert script 방식으로 재현
"""

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 3306))
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")


airtime_df = pd.read_csv("route_hour_airtime_stats.csv")


conn = pymysql.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME,
    charset="utf8mb4",
    autocommit=False  # 트랜잭션 제어
)

cursor = conn.cursor()


sql = """
INSERT INTO airtime (route, crs_dep_hour, airtime_mean)
VALUES (%s, %s, %s)
"""


BATCH_SIZE = 1000

try:
    batch = []

    for row in airtime_df.itertuples(index=False):
        batch.append((
            row.route,
            int(row.crs_dep_hour),
            float(row.airtime_mean) if pd.notna(row.airtime_mean) else None
        ))

        if len(batch) >= BATCH_SIZE:
            cursor.executemany(sql, batch)
            batch.clear()

    # 남은 데이터
    if batch:
        cursor.executemany(sql, batch)

    conn.commit()
    print("✅ Insert completed")

except Exception as e:
    conn.rollback()
    print("❌ Error:", e)

finally:
    cursor.close()
    conn.close()