import os
import urllib.request

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/1/hand_landmarker.task"
)
HAND_CONNECTIONS = [
    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),
    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),
    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),
    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),
    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (0, 17),
]
LANDMARK_NAMES = [
    "wrist",
    "thumb_cmc",
    "thumb_mcp",
    "thumb_ip",
    "thumb_tip",
    "index_finger_mcp",
    "index_finger_pip",
    "index_finger_dip",
    "index_finger_tip",
    "middle_finger_mcp",
    "middle_finger_pip",
    "middle_finger_dip",
    "middle_finger_tip",
    "ring_finger_mcp",
    "ring_finger_pip",
    "ring_finger_dip",
    "ring_finger_tip",
    "pinky_mcp",
    "pinky_pip",
    "pinky_dip",
    "pinky_tip",
]


def _ensure_model() -> None:
    if not os.path.exists(MODEL_PATH):
        print("Downloading hand landmarker model...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)


def _serialize_hand_landmarks(hand_landmarks, frame_width: int, frame_height: int) -> list[dict]:
    serialized = []
    for landmark_index, landmark in enumerate(hand_landmarks):
        serialized.append(
            {
                "index": landmark_index,
                "name": LANDMARK_NAMES[landmark_index],
                "x": round(float(landmark.x), 4),
                "y": round(float(landmark.y), 4),
                "z": round(float(landmark.z), 4),
                "pixel_x": int(landmark.x * frame_width),
                "pixel_y": int(landmark.y * frame_height),
            }
        )
    return serialized


def annotate_frame(frame, hand_landmarks_groups) -> cv2.typing.MatLike:
    annotated_image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    frame_height, frame_width = frame.shape[:2]

    for hand_landmarks in hand_landmarks_groups:
        points = [
            (int(landmark.x * frame_width), int(landmark.y * frame_height))
            for landmark in hand_landmarks
        ]
        for point in points:
            cv2.circle(annotated_image, point, 3, (0, 255, 0), -1)
        for start_index, end_index in HAND_CONNECTIONS:
            cv2.line(annotated_image, points[start_index], points[end_index], (0, 200, 0), 1)

    return annotated_image


def prepare_frame(frame, detector) -> dict:
    resized = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=resized)
    detection_result = detector.detect(mp_image)
    hand_landmarks_groups = detection_result.hand_landmarks

    frame_height, frame_width = resized.shape[:2]
    hands = [
        {
            "hand_index": hand_index,
            "landmarks": _serialize_hand_landmarks(hand_landmarks, frame_width, frame_height),
        }
        for hand_index, hand_landmarks in enumerate(hand_landmarks_groups)
    ]

    return {
        "frame": resized,
        "annotated_frame": annotate_frame(resized, hand_landmarks_groups),
        "hands": hands,
        "hand_count": len(hands),
        "landmarks_detected": sum(len(hand["landmarks"]) for hand in hands),
    }


def prepare_frames(frames: list) -> list:
    _ensure_model()
    processed = []

    options = mp_vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=MODEL_PATH),
        num_hands=2,
        min_hand_detection_confidence=0.5,
        running_mode=mp_vision.RunningMode.IMAGE,
    )

    with mp_vision.HandLandmarker.create_from_options(options) as detector:
        for frame in frames:
            processed.append(prepare_frame(frame, detector))

    if processed:
        print(f"Preprocessed {len(processed)} frames")
        print(f"New frame shape: {processed[0]['frame'].shape}")

    return processed

