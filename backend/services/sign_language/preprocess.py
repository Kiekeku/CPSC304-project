
import cv2
import os
import mediapipe as mp

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

def prepare_frame(frame, hands):
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
    results = hands.process(resized)

    return {
        "frame" : resized,
        "landmarks" : results.multi_hand_landmarks
    }

def prepare_frames(frames: list) -> list:
    """
    prepares a list of frames
    """
    processed = []
    with mp_hands.Hands(
        static_image_mode=True, 
        max_num_hands=2, 
        min_detection_confidence=0.5 # need to test detection conf
    ) as hands:
        for frame in frames:
            processed.append(prepare_frame(frame))

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
            for hand_landmarks in landmarks:
                mp_drawing.draw_landmarks(annotated_image, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        filename = os.path.join(output_dir, f"frame_{i:04d}.jpg")
        cv2.imwrite(filename, BGR_image)

    print(f"Saved {len(frames)} frames to {output_dir}/")

if __name__ == "__main__":
    from capture import extract_frames

    frames = extract_frames("test_video.mp4")
    processed = prepare_frames(frames)
    save_frames(processed, "test_frames_output")