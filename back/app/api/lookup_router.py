from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List

from back.app.infra.repo.airport_info_repo import find_all_active_airports
from back.app.infra.repo.airline_repo import find_all_airlines
from back.app.infra.db import get_conn

router = APIRouter(prefix="/lookup")


class CodeNameItem(BaseModel):
    code: str
    name: str


class CodeNameListResponse(BaseModel):
    items: List[CodeNameItem]

@router.get("/airports", response_model=CodeNameListResponse)
def get_airports(conn=Depends(get_conn)):
    rows = find_all_active_airports(conn)
    return {"items": [
        {
            "code": row[0],
            "name": row[1]
        } for row in rows
    ]}

@router.get("/airlines", response_model=CodeNameListResponse)
def get_airlines(conn=Depends(get_conn)):
    rows = find_all_airlines(conn)
    return {"items": [
        {
            "code": row[0],
            "name": row[1]
        } for row in rows
    ]}