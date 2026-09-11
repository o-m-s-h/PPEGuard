from fastapi import APIRouter, File, Query, Request, UploadFile

from app.api.uploads import process_upload
from app.services.image_inference import detect_image

router = APIRouter(prefix="/detect", tags=["Detection"])


@router.post("/image")
def image(request: Request, file: UploadFile = File(...), conf: float = Query(0.25, ge=0, le=1)):
    """Upload an image; receive violations and annotated JPEG/report download URLs."""
    return process_upload(request, file, conf, detect_image, {".jpg", ".jpeg", ".png", ".bmp", ".webp"})
