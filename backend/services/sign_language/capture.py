import cv2

def get_video_info(video_path: str) -> dict:
    """
    open a video file and return basic information about it
    """
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)  # frames per second
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps  # seconds

    cap.release()

    return {
        "total_frames": total_frames,
        "fps": fps,
        "width": width,
        "height": height,
        "duration_seconds": round(duration, 2),
    }

def extract_frames(video_path: str, frame_interval: int=5) -> list:
    """
    read every nth frame from a video
    note: for frame_interval = x, grab 1 frame per every x frames
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open video: {video_path}")

    frames = []
    frame_count = 0 

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames.append(frame_rgb)

        frame_count += 1

    cap.release()

    print(f"Total frames in video: {frame_count}")
    print(f"Frames extracted (every {frame_interval}): {len(frames)}")
    print(f"Each frame shape: {frames[0].shape}")  

    return frames

if __name__ == "__main__":
    info = get_video_info("test_video.mp4")
    print(info)

    frames = extract_frames("test_video.mp4")
