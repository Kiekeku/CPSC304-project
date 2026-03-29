import json
from pathlib import Path

import cv2

ANALYSES_DIR = Path(__file__).resolve().parents[2] / "uploads" / "analyses"
ANALYSES_DIR.mkdir(parents=True, exist_ok=True)
METADATA_FILENAME = "metadata.json"
VIDEO_FILENAME = "source"
FRAME_DIRNAME = "frames"


def _analysis_dir(analysis_id: str) -> Path:
    return ANALYSES_DIR / analysis_id


def create_analysis_record(
    analysis_id: str,
    source_path: Path,
    original_filename: str,
    info: dict,
    processed_frames: list,
) -> dict:
    analysis_dir = _analysis_dir(analysis_id)
    frames_dir = analysis_dir / FRAME_DIRNAME
    analysis_dir.mkdir(parents=True, exist_ok=True)
    frames_dir.mkdir(parents=True, exist_ok=True)

    source_extension = source_path.suffix or Path(original_filename).suffix or ".mp4"
    stored_video_name = f"{VIDEO_FILENAME}{source_extension}"
    stored_video_path = analysis_dir / stored_video_name
    stored_video_path.write_bytes(source_path.read_bytes())

    frame_entries = []
    frame_interval = max(1, int(info.get("frame_interval", 1)))
    fps = float(info.get("fps") or 0)

    for frame_position, processed_frame in enumerate(processed_frames):
        frame_filename = f"frame_{frame_position:04d}.jpg"
        frame_path = frames_dir / frame_filename
        cv2.imwrite(str(frame_path), processed_frame["annotated_frame"])

        original_frame_index = frame_position * frame_interval
        timestamp_seconds = round(original_frame_index / fps, 3) if fps else None
        frame_entries.append(
            {
                "frame_position": frame_position,
                "original_frame_index": original_frame_index,
                "timestamp_seconds": timestamp_seconds,
                "hand_count": processed_frame["hand_count"],
                "landmarks_detected": processed_frame["landmarks_detected"],
                "hands": processed_frame["hands"],
                "image_url": f"/sign-language/analyses/{analysis_id}/frames/{frame_filename}",
            }
        )

    metadata = {
        "analysis_id": analysis_id,
        "filename": original_filename,
        "video_url": f"/sign-language/analyses/{analysis_id}/video/{stored_video_name}",
        "total_frames": info.get("total_frames"),
        "fps": info.get("fps"),
        "duration_seconds": info.get("duration_seconds"),
        "width": info.get("width"),
        "height": info.get("height"),
        "frame_interval": frame_interval,
        "frames_extracted": len(frame_entries),
        "frames_with_hands": sum(1 for frame in frame_entries if frame["hand_count"] > 0),
        "frames": frame_entries,
    }

    metadata_path = analysis_dir / METADATA_FILENAME
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def update_analysis_record(analysis_id: str, updates: dict) -> dict:
    metadata = read_analysis_record(analysis_id)
    metadata.update(updates)
    metadata_path = _analysis_dir(analysis_id) / METADATA_FILENAME
    metadata_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def read_analysis_record(analysis_id: str) -> dict:
    metadata_path = _analysis_dir(analysis_id) / METADATA_FILENAME
    return json.loads(metadata_path.read_text(encoding="utf-8"))


def list_analysis_records() -> list[dict]:
    records = []
    for metadata_path in sorted(ANALYSES_DIR.glob(f"*/{METADATA_FILENAME}"), reverse=True):
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        records.append(
            {
                "analysis_id": metadata["analysis_id"],
                "filename": metadata["filename"],
                "duration_seconds": metadata.get("duration_seconds"),
                "fps": metadata.get("fps"),
                "total_frames": metadata.get("total_frames"),
                "frames_extracted": metadata.get("frames_extracted"),
                "frames_with_hands": metadata.get("frames_with_hands"),
                "recording_id": metadata.get("recording_id"),
                "transcript_id": metadata.get("transcript_id"),
            }
        )
    return records


def get_analysis_video_path(analysis_id: str, filename: str) -> Path:
    return _analysis_dir(analysis_id) / filename


def get_analysis_frame_path(analysis_id: str, filename: str) -> Path:
    return _analysis_dir(analysis_id) / FRAME_DIRNAME / filename

