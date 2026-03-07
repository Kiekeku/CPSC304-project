from fastapi import APIRouter

from models.schemas import PredictRequest
from services.ml_service import predict

router = APIRouter(prefix="/ml", tags=["ml"])


@router.post("/predict")
def post_predict(payload: PredictRequest) -> dict:
    return predict(payload.model_dump())
