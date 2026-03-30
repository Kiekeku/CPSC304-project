import json
import pickle
import uuid
from datetime import datetime

import cv2
import numpy as np
import oracledb

from db import get_connection
from services.sign_language.preprocess import prepare_frames
from services.sign_language.capture import extract_frames

def create_dataset(name: str) -> dict:
    dataset_id = str(uuid.uuid4())[:8]
    now = datetime.utcnow()
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO Gesture_Model (dataset_id, dataset_name, gesture_labels, created_at)
               VALUES (:1, :2, :3, :4)""",
            [dataset_id, name, json.dumps([]), now],
        )
        conn.commit()
    return {"dataset_id": dataset_id, "name": name, "gestures": [], "trained": False}

def list_datasets() -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT dataset_id, dataset_name, gesture_labels, trained_at FROM Gesture_Model"
            " ORDER BY created_at ASC"
        )
        rows = cur.fetchall()
    return [
        {
            "dataset_id": r[0],
            "name": r[1],
            "gestures": json.loads(r[2]) if r[2] else [],
            "trained": r[3] is not None,
        }
        for r in rows
    ]

def get_dataset_detail(dataset_id: str) -> dict:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT dataset_id, dataset_name, gesture_labels, trained_at"
            " FROM Gesture_Model WHERE dataset_id = :1",
            [dataset_id],
        )
        row = cur.fetchone()
        if not row:
            raise FileNotFoundError(f"Dataset '{dataset_id}' not found.")

        labels = json.loads(row[2]) if row[2] else []

        label_details = []
        for label in labels:
            cur.execute(
                "SELECT COUNT(*) FROM Gesture_Sample WHERE dataset_id = :1 AND gesture_label = :2",
                [dataset_id, label],
            )
            count = cur.fetchone()[0]
            label_details.append({"label": label, "sample_count": count})

    return {
        "dataset_id": row[0],
        "name": row[1],
        "gestures": labels,
        "trained": row[3] is not None,
        "trained_at": row[3].isoformat() if row[3] else None,
        "label_details": label_details,
    }