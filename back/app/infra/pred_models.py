# back/app/infra/pred_models.py
from fastapi import Depends
from back.app.infra.db import get_conn

import json


def find_model(conn, name: str):
    with conn.cursor() as cur:
        cur.execute("SELECT model FROM pred_models WHERE name=%s", (name,))
        model_json = cur.fetchone()

        if not model_json:
            return None
        
        return json.load(model_json)
    
def save_model(conn, name: str, model: dict):
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO pred_models (name, model) VALUES (%s, %s)",
                (name, json.dumps(model))
            )
            return cur.lastrowid

    except Exception as e:
        # 중복 키 에러만 잡기 (MySQL error code 1062)
        if hasattr(e, "args") and e.args[0] == 1062:
            return None
        raise