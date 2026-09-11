from fastapi import APIRouter, File, Query, Request, UploadFile

from app.api.uploads import process_upload
from app.services.video_inference import detect_video

router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post("/video")
def video(request: Request, file: UploadFile = File(...), conf: float = Query(0.25, ge=0, le=1)):
    """Upload a video; receive grouped violation events and MP4/report download URLs."""
    return process_upload(request, file, conf, detect_video, {".mp4", ".avi", ".mov", ".mkv", ".webm", ".m4v"})
