
import cv2
import os
import urllib.request
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision as mp_vision

_MODEL_PATH = os.path.join(os.path.dirname(__file__), "hand_landmarker.task")
_MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"

def _ensure_model():
    if not os.path.exists(_MODEL_PATH):
        print(f"Downloading hand landmarker model...")
        urllib.request.urlretrieve(_MODEL_URL, _MODEL_PATH)

def prepare_frame(frame, detector):
    """
    prepares a raw frame for easier analysis
    - resize
    - convert to grayscale
    - extract handmarks using mediapipe
    """

    resized = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
    # gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    # result = clahe.apply(gray)
    # return result
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=resized)
    result = detector.detect(mp_image)

    return {
        "frame" : resized,
        "landmarks" : result.hand_landmarks
    }

def prepare_frames(frames: list) -> list:
    """
    prepares a list of frames
    """
    _ensure_model()
    processed = []
    
    options = mp_vision.HandLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=_MODEL_PATH),
        num_hands=2,
        min_hand_detection_confidence=0.5,
        running_mode=mp_vision.RunningMode.IMAGE,
    )
    with mp_vision.HandLandmarker.create_from_options(options) as detector:
        for frame in frames:
            processed.append(prepare_frame(frame, detector))

    print(f"Preprocessed {len(processed)} frames")
    print(f"New frame shape: {processed[0]["frame"].shape}") 
    return processed

def save_frames(frames: list, output_dir: str) -> None:
    """
    save frames as images for testing
    """
    os.makedirs(output_dir, exist_ok=True)

    for i, data in enumerate(frames):
        frame = data["frame"]
        landmarks = data["landmarks"]

        BGR_image = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

        if landmarks:
            h, w = annotated_image.shape[:2]
            CONNECTIONS = [
                (0,1),(1,2),(2,3),(3,4),
                (0,5),(5,6),(6,7),(7,8),
                (0,9),(9,10),(10,11),(11,12),
                (0,13),(13,14),(14,15),(15,16),
                (0,17),(17,18),(18,19),(19,20),
                (5,9),(9,13),(13,17),
            ]
            # These are the connections for each finger, as per MediaPipe documentation
            # https://chuoling.github.io/mediapipe/solutions/hands.html
            for hand_landmarks in landmarks:
                pts = [(int(lm.x * w), int(lm.y * h)) for lm in hand_landmarks]
                for pt in pts:
                    cv2.circle(annotated_image, pt, 3, (0, 255, 0), -1)
                for a, b in CONNECTIONS:
                    cv2.line(annotated_image, pts[a], pts[b], (0, 200, 0), 1)

        filename = os.path.join(output_dir, f"frame_{i:04d}.jpg")
        cv2.imwrite(filename, BGR_image)

    print(f"Saved {len(frames)} frames to {output_dir}/")

if __name__ == "__main__":
    from capture import extract_frames

    frames = extract_frames("test_video.mp4")
    processed = prepare_frames(frames)
    save_frames(processed, "test_frames_output")