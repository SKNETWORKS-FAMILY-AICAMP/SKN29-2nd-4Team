from fastapi import APIRouter, Depends
from pydantic import BaseModel

from back.app.infra.db import get_tx
from back.app.infra.pred_models import save_model


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
                "status": "failed",
                "reason": f"name '{request.name}' already exsist"
            }

        return {
            "status": "ok",
            "name": request.name,
            "id": model_id,
        }
