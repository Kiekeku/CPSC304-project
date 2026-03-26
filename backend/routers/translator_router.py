import shutil
from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, HTTPException, UploadFile, File

from services.sign_language.capture import extract_frames, get_video_info
from services.sign_language.preprocess import preprocess_frames

router = APIRouter(prefix="/sign-language", tags=["sign-language"])

UPLOAD_DIR = Path("uploads") # temporary upload folder
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/analyze")
async def analyze_video(file: UploadFile = File(...)):
    """
    accept a video upload, extract frames, and preprocess them
    """