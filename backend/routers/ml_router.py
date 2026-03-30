from fastapi import APIRouter
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from models.schemas import (
    PredictRequest,
    CreateDatasetRequest,
    AddGestureLabelRequest,
    RecognizeRequest,
)
from services.ml_service import (
    predict,
    svc_create_dataset,
    svc_list_datasets,
    svc_get_dataset,
    svc_add_label,
    svc_ingest_video,
    svc_train,
    svc_recognize,
)

router = APIRouter(prefix="/ml", tags=["ml"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/predict")
def post_predict(payload: PredictRequest) -> dict:
    return predict(payload.model_dump())

@router.post("/datasets", status_code=201)
def create_dataset(body: CreateDatasetRequest) -> dict:
    return svc_create_dataset(body.name)


@router.get("/datasets")
def list_datasets() -> dict:
    return {"datasets": svc_list_datasets()}


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str) -> dict:
    try:
        return svc_get_dataset(dataset_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/datasets/{dataset_id}/gestures", status_code=201)
def add_gesture(dataset_id: str, body: AddGestureLabelRequest) -> dict:
    try:
        return svc_add_label(dataset_id, body.label)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc