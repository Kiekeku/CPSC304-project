import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, HTTPException, UploadFile, File

from services.sign_language.capture import extract_frames, get_video_info
from services.sign_language.preprocess import prepare_frames
from services.sign_language.store import save_recording_transcript


router = APIRouter(prefix="/sign-language", tags=["sign-language"])

UPLOAD_DIR = Path("uploads") # temporary upload folder
UPLOAD_DIR.mkdir(exist_ok=True)


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
        frames = extract_frames(tmp_path)
        processed = prepare_frames(frames)
        # TODO run ML model on processed frames (justin's part), rn keep as temp "unknown" to test db
        transcript_text = "unknown"

        # hardcoded user_id=1 until login is ready
        ids = save_recording_transcript(
            user_id=1,
            recording_name=file.filename,
            fps=info["fps"],
            duration=info["duration_seconds"],
            transcript_text=transcript_text,
        )

        return {
            "message": "Video processed and saved successfully",
            "filename": file.filename,
            "total_frames": info["total_frames"],
            "fps": info["fps"],
            "duration_seconds": info["duration_seconds"],
            "frames_extracted": len(processed),
            "recording_id": ids["recording_id"],
            "transcript_id": ids["transcript_id"],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(type(e).__name__) + ": " + str(e))

    finally:
        Path(tmp_path).unlink(missing_ok=True)