import hashlib
import os
import shutil

from fastapi import APIRouter, UploadFile, File

from app import storage
from app.schemas import UploadResponse

router = APIRouter()

UPLOAD_DIR = "uploaded_media"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload", response_model=UploadResponse)
async def upload_media(file: UploadFile = File(...)):
    content_id = storage.new_id("content")
    dest_path = os.path.join(UPLOAD_DIR, f"{content_id}_{file.filename}")

    with open(dest_path, "wb") as out:
        shutil.copyfileobj(file.file, out)

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