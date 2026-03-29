from datetime import datetime
import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from services.sign_language.capture import extract_frames, get_video_info
from services.sign_language.preprocess import prepare_frames
from services.sign_language.analysis_store import (
    create_analysis_record,
    get_analysis_frame_path,
    get_analysis_video_path,
    list_analysis_records,
    read_analysis_record,
    update_analysis_record,
)
from services.sign_language.store import save_recording_transcript


router = APIRouter(prefix="/sign-language", tags=["sign-language"])

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
FRAME_INTERVAL = 5


@router.get("/analyses")
def get_analyses() -> dict:
    return {"analyses": list_analysis_records()}


@router.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: str) -> dict:
    try:
        return read_analysis_record(analysis_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Analysis not found.") from exc


@router.get("/analyses/{analysis_id}/video/{filename}")
def get_analysis_video(analysis_id: str, filename: str) -> FileResponse:
    video_path = get_analysis_video_path(analysis_id, filename)
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video not found.")
    return FileResponse(video_path)


@router.get("/analyses/{analysis_id}/frames/{filename}")
def get_analysis_frame(analysis_id: str, filename: str) -> FileResponse:
    frame_path = get_analysis_frame_path(analysis_id, filename)
    if not frame_path.exists():
        raise HTTPException(status_code=404, detail="Frame image not found.")
    return FileResponse(frame_path)


@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """
    accept a video upload, extract frames, and preprocess them
    """

    suffix = Path(file.filename).suffix
    with NamedTemporaryFile(delete=False, suffix=suffix, dir=UPLOAD_DIR) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        info = get_video_info(tmp_path)
        info["frame_interval"] = FRAME_INTERVAL
        frames = extract_frames(tmp_path, frame_interval=FRAME_INTERVAL)
        processed = prepare_frames(frames)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        stem = Path(file.filename).stem
        suffix_ext = Path(file.filename).suffix
        analysis_id = f"{stem}_{timestamp}"
        analysis_metadata = create_analysis_record(
            analysis_id=analysis_id,
            source_path=Path(tmp_path),
            original_filename=file.filename,
            info=info,
            processed_frames=processed,
        )

        # TODO run ML model on processed frames (justin's part), rn keep as temp "unknown" to test db
        transcript_text = "unknown"

        # assign a unique id to every video
        unique_name = f"{stem}_{timestamp}{suffix_ext}"

        # hardcoded user_id=1 until login is ready
        ids = save_recording_transcript(
            user_id=1,
            recording_name=unique_name,
            fps=info["fps"],
            duration=info["duration_seconds"],
            transcript_text=transcript_text,
        )

        analysis_metadata = update_analysis_record(
            analysis_id,
            {
                "message": "Video processed and saved successfully",
                "recording_id": ids["recording_id"],
                "transcript_id": ids["transcript_id"],
            },
        )

        return {
            **analysis_metadata,
            "message": "Video processed and saved successfully",
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(type(e).__name__) + ": " + str(e))

    finally:
        Path(tmp_path).unlink(missing_ok=True)
