from fastapi import APIRouter, HTTPException

from app import storage

router = APIRouter()


@router.get("/result/{analysis_id}")
async def get_result(analysis_id: str):
    record = storage.get_analysis(analysis_id)
    if record is None:
        raise HTTPException(status_code=404, detail="analysis_id not found.")
    return record["final_result"]