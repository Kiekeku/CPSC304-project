import json
import pickle
from datetime import datetime
from pathlib import Path

import numpy as np

from db import get_connection
from services.sign_language.capture import extract_frames
from services.sign_language.preprocess import prepare_frames

GESTURE_DATA_DIR = Path(__file__).resolve().parent.parent / "gesture_data"
GESTURE_DATA_DIR.mkdir(exist_ok=True)

DEFAULT_USER_ID = 1


def _artifact_ref(*parts: str) -> str:
    return "/".join(parts)[:255]


def _next_id(cursor, tables, column):
    parts = [f"SELECT NVL(MAX({column}), 0) AS m FROM {t}" for t in tables]
    cursor.execute(f"SELECT MAX(m) + 1 FROM ({' UNION ALL '.join(parts)})")
    return cursor.fetchone()[0] or 1


def _ensure_data_dir(dataset_id: int) -> Path:
    data_dir = GESTURE_DATA_DIR / str(dataset_id)
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


def create_dataset(name: str) -> dict:
    with get_connection() as conn:
        cur = conn.cursor()
        model_id = _next_id(cur, ["Trained_Machine_Learning_Model"], "model_id")
        
        cur.execute(
            "INSERT INTO Trained_Machine_Learning_Model"
            " (model_id, accuracy, hyperparameter, model_type)"
            " VALUES (:1, :2, :3, :4)",
            [model_id, 0, 5, name],
        )

        conn.commit()

    (GESTURE_DATA_DIR / str(model_id)).mkdir(exist_ok=True)

    return {"dataset_id": model_id, "name": name, "gestures": [], "trained": False}


def list_datasets() -> list[dict]:
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute(
            "SELECT model_id, model_type, accuracy, hyperparameter, handmark_id"
            " FROM Trained_Machine_Learning_Model ORDER BY model_id"
        )

        rows = cur.fetchall()
    return [
        {
            "dataset_id": r[0],
            "name": r[1],
            "accuracy": r[2],
            "k": r[3],
            "trained": r[4] is not None,
        }
        for r in rows
    ]


def get_dataset_detail(dataset_id: int) -> dict:
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute(
            "SELECT model_id, model_type, accuracy, hyperparameter, handmark_id"
            " FROM Trained_Machine_Learning_Model WHERE model_id = :1",
            [dataset_id],
        )

        row = cur.fetchone()

        if not row:
            raise FileNotFoundError(f"Dataset {dataset_id} not found.")

        cur.execute(
            """SELECT cd.gesture, cd.def_id, ph2.number_of_frames
               FROM Calibrated_Definition cd
               JOIN Predicted_Gesture_Handmark1 ph1 ON ph1.def_id = cd.def_id
               JOIN Predicted_Gesture_Handmark2 ph2 ON ph2.def_id = cd.def_id
               WHERE ph1.model_id = :1""",
            [dataset_id],
        )
        label_rows = cur.fetchall()

    label_details = []
    data_dir = GESTURE_DATA_DIR / str(dataset_id)

    for label, def_id, db_frame_count in label_rows:
        sample_file = data_dir / f"{label}.json"

        if sample_file.exists():
            samples = json.loads(sample_file.read_text())
            sample_count = len(samples)
        else:
            sample_count = 0

        label_details.append({"label": label, "def_id": def_id, "sample_count": sample_count})

    return {
        "dataset_id": row[0],
        "name": row[1],
        "accuracy": row[2],
        "k": row[3],
        "trained": row[4] is not None,
        "gestures": [l["label"] for l in label_details],
        "label_details": label_details,
    }

    
def add_gesture_label(dataset_id: int, label: str) -> dict:
    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute(
            "SELECT model_id FROM Trained_Machine_Learning_Model WHERE model_id = :1",
            [dataset_id],
        )
        if not cur.fetchone():
            raise FileNotFoundError(f"Dataset {dataset_id} not found.")

        cur.execute(
            """SELECT cd.def_id FROM Calibrated_Definition cd
               JOIN Predicted_Gesture_Handmark1 ph1 ON ph1.def_id = cd.def_id
               WHERE ph1.model_id = :1 AND cd.gesture = :2""",
            [dataset_id, label],
        )
        if cur.fetchone():
            raise ValueError(f"Label '{label}' already exists in this dataset.")

        def_id = _next_id(
            cur,
            ["Calibrated_Definition", "Predicted_Gesture_Handmark2"],
            "def_id",
        )
        handmark_id = _next_id(cur, ["Predicted_Gesture_Handmark1"], "handmark_id")

        cur.execute(
            "INSERT INTO Predicted_Gesture_Handmark2"
            " (def_id, number_of_frames, x_position, y_position)"
            " VALUES (:1, :2, :3, :4)",
            [def_id, 0, str(def_id), "0.0"],
        )
        cur.execute(
            "INSERT INTO Calibrated_Definition"
            " (def_id, user_id, gesture, def_name, description)"
            " VALUES (:1, :2, :3, :4, :5)",
            [def_id, DEFAULT_USER_ID, label, label, f"dataset:{dataset_id}"],
        )
        cur.execute(
            "INSERT INTO Predicted_Gesture_Handmark1 (handmark_id, def_id, model_id)"
            " VALUES (:1, :2, :3)",
            [handmark_id, def_id, dataset_id],
        )

        conn.commit()

    return {"dataset_id": dataset_id, "label": label, "def_id": def_id}


def _landmarks_to_vector(landmarks: list[dict]) -> list[float]:
    vec = []
    for lm in sorted(landmarks, key=lambda l: l["index"]):
        vec.extend([lm["x"], lm["y"], lm["z"]])
    return vec



def ingest_video(video_path: str, dataset_id: int, label: str) -> int:
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

    sample_file = GESTURE_DATA_DIR / str(dataset_id) / f"{label}.json"
    existing = json.loads(sample_file.read_text()) if sample_file.exists() else []
    sample_file.write_text(json.dumps(existing + vectors))

    total = len(existing) + len(vectors)
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """UPDATE Predicted_Gesture_Handmark2 SET number_of_frames = :1
               WHERE def_id = (
                   SELECT cd.def_id FROM Calibrated_Definition cd
                   JOIN Predicted_Gesture_Handmark1 ph ON ph.def_id = cd.def_id
                   WHERE ph.model_id = :2 AND cd.gesture = :3
               )""",
            [total, dataset_id, label],
        )
        conn.commit()

    return len(vectors)

    
def train_model(dataset_id: int) -> dict:
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.model_selection import cross_val_score

    data_dir = GESTURE_DATA_DIR / str(dataset_id)
    X, y = [], []

    for sample_file in data_dir.glob("*.json"):
        label = sample_file.stem
        raw = json.loads(sample_file.read_text())
        valid = [v for v in raw if isinstance(v, list) and len(v) == 63]
        X.extend(valid)
        y.extend([label] * len(valid))

    if not X:
        raise ValueError("No training samples found. Upload videos first.")

    unique_labels = sorted(set(y))
    if len(unique_labels) < 2:
        raise ValueError("Need at least 2 gesture labels with samples to train.")

    X = np.array(X, dtype=float)
    k = min(5, len(X))
    clf = KNeighborsClassifier(n_neighbors=k, metric="euclidean", weights="distance")
    clf.fit(X, y)

    accuracy_pct = 0

    if len(X) >= 10:
        scores = cross_val_score(clf, X, y, cv=min(5, len(X)))
        accuracy_pct = int(round(float(scores.mean()) * 100))

    pkl_path = data_dir / "model.pkl"
    pkl_path.write_bytes(pickle.dumps(clf))

    with get_connection() as conn:
        cur = conn.cursor()

        cur.execute(
            "UPDATE Trained_Machine_Learning_Model"
            " SET accuracy = :1, hyperparameter = :2"
            " WHERE model_id = :3",
            [accuracy_pct, k, dataset_id],
        )
        cur.execute(
            "SELECT handmark_id FROM Predicted_Gesture_Handmark1"
            " WHERE model_id = :1 AND ROWNUM = 1",
            [dataset_id],
        )

        first_hm = cur.fetchone()

        if first_hm:
            cur.execute(
                "UPDATE Trained_Machine_Learning_Model SET handmark_id = :1"
                " WHERE model_id = :2",
                [first_hm[0], dataset_id],
            )

        for label in unique_labels:
            label_vecs = np.array(
                [v for v, lbl in zip(X, y) if lbl == label], dtype=float
            )

            mean = label_vecs.mean(axis=0)
            summary_payload = {
                "label": label,
                "sample_count": int(len(label_vecs)),
                "mean_landmarks": mean.tolist(),
            }
            summary_path = data_dir / f"{label}.summary.json"
            summary_path.write_text(json.dumps(summary_payload))

            sample_ref = _artifact_ref("gesture_data", str(dataset_id), f"{label}.json")
            summary_ref = _artifact_ref("gesture_data", str(dataset_id), f"{label}.summary.json")

            cur.execute(
                """UPDATE Predicted_Gesture_Handmark2 SET x_position = :1, y_position = :2
                   WHERE def_id = (
                       SELECT cd.def_id FROM Calibrated_Definition cd
                       JOIN Predicted_Gesture_Handmark1 ph ON ph.def_id = cd.def_id
                       WHERE ph.model_id = :3 AND cd.gesture = :4
                   )""",
                [sample_ref, summary_ref, dataset_id, label],
            )

        conn.commit()

    return {
        "dataset_id": dataset_id,
        "labels": unique_labels,
        "sample_count": len(X),
        "accuracy_pct": accuracy_pct,
        "k": k,
    }

def recognize_gesture(dataset_id: int, landmarks: list[dict]) -> dict:
    pkl_path = GESTURE_DATA_DIR / str(dataset_id) / "model.pkl"

    if not pkl_path.exists():
        raise ValueError(
            f"No trained model for dataset {dataset_id}."
        )

    clf = pickle.loads(pkl_path.read_bytes())
    vec = _landmarks_to_vector(landmarks)

    if len(vec) != 63:
        raise ValueError("Expected 21 landmarks.")

    X = np.array([vec])
    label = clf.predict(X)[0]
    proba = clf.predict_proba(X)[0] if hasattr(clf, "predict_proba") else None
    confidence = round(float(max(proba)), 4) if proba is not None else None

    return {"label": label, "confidence": confidence}

    
def recognize_from_frame(dataset_id: int, frame_bytes: bytes) -> dict:
    from services.sign_language.preprocess import prepare_frames

    nparr = np.frombuffer(frame_bytes, np.uint8)
    frame_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    if frame_bgr is None:
        raise ValueError("Could not decode image frame.")

    processed = prepare_frames([frame_bgr])
    if not processed:
        return {"label": None, "confidence": None, "hand_count": 0}

    hands = processed[0].get("hands", [])
    if not hands:
        return {"label": None, "confidence": None, "hand_count": 0}

    vec = _landmarks_to_vector(hands[0]["landmarks"])
    if len(vec) != 63:
        return {"label": None, "confidence": None, "hand_count": len(hands)}

    pkl_path = GESTURE_DATA_DIR / str(dataset_id) / "model.pkl"
    if not pkl_path.exists():
        raise ValueError(f"No trained model for dataset {dataset_id}. Train first.")

    clf = pickle.loads(pkl_path.read_bytes())
    X = np.array([vec])
    label = clf.predict(X)[0]
    proba = clf.predict_proba(X)[0] if hasattr(clf, "predict_proba") else None
    confidence = round(float(max(proba)), 4) if proba is not None else None

    return {"label": label, "confidence": confidence, "hand_count": len(hands)}
