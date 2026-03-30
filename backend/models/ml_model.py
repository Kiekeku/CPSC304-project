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

    
def add_gesture_label(dataset_id: str, label: str) -> dict:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT gesture_labels FROM Gesture_Model WHERE dataset_id = :1",
            [dataset_id],
        )
        row = cur.fetchone()
        if not row:
            raise FileNotFoundError(f"Dataset '{dataset_id}' not found.")
        labels = json.loads(row[0]) if row[0] else []
        if label in labels:
            raise ValueError(f"Label '{label}' already exists.")
        labels.append(label)
        cur.execute(
            "UPDATE Gesture_Model SET gesture_labels = :1 WHERE dataset_id = :2",
            [json.dumps(labels), dataset_id],
        )
        conn.commit()
    return {"dataset_id": dataset_id, "gestures": labels}


def _landmarks_to_vector(landmarks: list[dict]) -> list[float]:
    vec = []
    for lm in sorted(landmarks, key=lambda l: l["index"]):
        vec.extend([lm["x"], lm["y"], lm["z"]])
    return vec


def ingest_video(video_path: str, dataset_id: str, label: str) -> int:
    frames = extract_frames(video_path, frame_interval=3)
    processed = prepare_frames(frames)

    vectors = []
    for frame_data in processed:
        for hand in frame_data.get("hands", []):
            vec = _landmarks_to_vector(hand["landmarks"])
            if len(vec) == 63:
                vectors.append(vec)

    if not vectors:
        return 0

    with get_connection() as conn:
        cur = conn.cursor()
        cur.executemany(
            "INSERT INTO Gesture_Sample (dataset_id, gesture_label, landmarks)"
            " VALUES (:1, :2, :3)",
            [[dataset_id, label, json.dumps(v)] for v in vectors],
        )
        conn.commit()

    return len(vectors)

    
def train_model(dataset_id: str) -> dict:
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import cross_val_score

    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT gesture_label, landmarks FROM Gesture_Sample WHERE dataset_id = :1",
            [dataset_id],
        )
        rows = cur.fetchall()

    if not rows:
        raise ValueError("No training samples found. Upload videos first.")

    X = np.array([json.loads(r[1]) for r in rows], dtype=float)
    y = [r[0] for r in rows]

    unique_labels = sorted(set(y))
    if len(unique_labels) < 2:
        raise ValueError("Need at least 2 gesture labels with samples to train.")

    k = min(5, len(X))
    clf = KNeighborsClassifier(n_neighbors=k, metric="euclidean", weights="distance")
    clf.fit(X, y)

    accuracy = None
    if len(X) >= 10:
        scores = cross_val_score(clf, X, y, cv=min(5, len(X)))
        accuracy = round(float(scores.mean()), 4)

    model_blob = pickle.dumps(clf)

    with get_connection() as conn:
        cur = conn.cursor()
        blob_var = conn.cursor().var(oracledb.BLOB)
        blob_var.setvalue(0, model_blob)
        cur.execute(
            "UPDATE Gesture_Model SET model_pickle = :1, trained_at = :2"
            " WHERE dataset_id = :3",
            [model_blob, datetime.utcnow(), dataset_id],
        )
        conn.commit()

    return {
        "dataset_id": dataset_id,
        "labels": unique_labels,
        "sample_count": len(X),
        "accuracy_cv": accuracy,
    }

def recognize_gesture(dataset_id: str, landmarks: list[dict]) -> dict:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT model_pickle FROM Gesture_Model WHERE dataset_id = :1",
            [dataset_id],
        )
        row = cur.fetchone()

    if not row or row[0] is None:
        raise ValueError("No trained model found for this dataset.")

    blob = row[0].read() if hasattr(row[0], "read") else row[0]
    clf = pickle.loads(blob)

    vec = _landmarks_to_vector(landmarks)
    if len(vec) != 63:
        raise ValueError("Expected 21 landmarks (63 values).")

    X = np.array([vec])
    label = clf.predict(X)[0]
    proba = clf.predict_proba(X)[0] if hasattr(clf, "predict_proba") else None
    confidence = round(float(max(proba)), 4) if proba is not None else None

    return {"label": label, "confidence": confidence}