from typing import Any


def predict(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "success": True,
        "prediction": None,
        "message": "ML model not implemented yet. Add logic in services/ml_service.py::predict",
        "input": payload,
    }
