from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import shutil

from AI.veritrace_detector import analyze_image


app = FastAPI(
    title="VeriTrace AI API"
)


UPLOAD_FOLDER = Path("AI/uploads")
UPLOAD_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():

    return {
        "message": "VeriTrace AI API is running"
    }


# ==========================================
# IMAGE ANALYSIS
# ==========================================

@app.post("/analyze")
async def analyze(
    file: UploadFile = File(...)
):

    file_path = UPLOAD_FOLDER / file.filename

    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    result = analyze_image(
        str(file_path)
    )

    return result