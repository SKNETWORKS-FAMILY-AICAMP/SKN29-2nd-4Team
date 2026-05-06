from contextlib import contextmanager
import pymysql

from back.app.config import settings


def get_connection():
    return pymysql.connect(
        host=settings.DB_HOST,
        port=settings.DB_PORT,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD.get_secret_value(),
        database=settings.DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.Cursor,
        autocommit=False,
    )


# FastAPI dependency
def get_conn():
    conn = get_connection()
    try:
        yield conn
    finally:
        conn.close()


@contextmanager
def get_tx():
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def test_connection():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")

        print("✅ DB Connection success")

    except Exception as e:
        print("❌ DB Connection failed:", e)
