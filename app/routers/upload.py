import hashlib
import os
import shutil

from fastapi import APIRouter, UploadFile, File, HTTPException

from app import storage
from app.schemas import UploadResponse

router = APIRouter()

UPLOAD_DIR = "uploaded_media"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".mp4", ".mov", ".avi", ".webm"}
MAX_FILE_SIZE_MB = 50
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


@router.post("/upload", response_model=UploadResponse)
async def upload_media(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    content_id = storage.new_id("content")
    dest_path = os.path.join(UPLOAD_DIR, f"{content_id}_{file.filename}")

    size = 0
    with open(dest_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            size += len(chunk)
            if size > MAX_FILE_SIZE_BYTES:
                out.close()
                os.remove(dest_path)
                raise HTTPException(
                    status_code=413,
                    detail=f"File exceeds {MAX_FILE_SIZE_MB}MB limit."
                )
            out.write(chunk)

    if size == 0:
        os.remove(dest_path)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    sha256 = _sha256_of_file(dest_path)
    perceptual_hash = None  # TODO(Vidhi): real perceptual hash later

    storage.save_content(content_id, file.filename, sha256, perceptual_hash, dest_path)

    return UploadResponse(
        content_id=content_id,
        filename=file.filename,
        sha256=sha256,
        perceptual_hash=perceptual_hash,
    )


def _sha256_of_file(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()