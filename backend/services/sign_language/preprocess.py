
import cv2

def prepare_frame(frame):
    """
    prepares a raw frame for easier analysis
    - resize
    - convert to grayscale
    """

    resized = cv2.resize(frame, (224, 224), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
    return gray

def prepare_frames(frame: list) -> list:
    """
    prepares a list of frames
    """
    processed = []
    for frame in frames:
        processed.append(prepare_frame(frame))

    print(f"Preprocessed {len(processed)} frames")
    print(f"New frame shape: {processed[0].shape}") 
    return processed

if __name__ == "__main__":
    from capture import extract_frames

    frames = extract_frames("test_video.mp4")
    processed = prepare_frames(frames)