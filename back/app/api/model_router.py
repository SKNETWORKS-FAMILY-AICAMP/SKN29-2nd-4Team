from fastapi import APIRouter, Depends
from pydantic import BaseModel

from back.app.infra.db import get_tx
from back.app.infra.repo.pred_model_repo import save_model


router = APIRouter(prefix="/models",)

class SaveModelRequest(BaseModel):
    name: str
    model: dict

@router.post("")
def save_model_request(request: SaveModelRequest):
    with get_tx() as conn:
        model_id = save_model(conn, request.name, request.model)

        if not model_id:
            return {
                "status": "bad request",
                "reason": f"name '{request.name}' already exsist"
            }

        return {
            "status": "ok",
            "name": request.name,
            "id": model_id,
        }
