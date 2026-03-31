from typing import Any

from models.ml_model import (
    create_dataset,
    list_datasets,
    get_dataset_detail,
    add_gesture_label,
    ingest_video,
    train_model,
    recognize_gesture,
    recognize_from_frame,
)

def predict(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "success": True,
        "prediction": None,
        "message": "Create a dataset of custom gestures for a machine-learning model.",
        "input": payload,
    }

svc_create_dataset = create_dataset
svc_list_datasets = list_datasets
svc_get_dataset = get_dataset_detail
svc_add_label = add_gesture_label
svc_ingest_video = ingest_video
svc_train = train_model
svc_recognize = recognize_gesture
svc_recognize_frame  = recognize_from_frame