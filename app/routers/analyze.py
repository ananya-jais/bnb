from fastapi import APIRouter, HTTPException

from app import storage
from app.schemas import AnalyzeRequest, FinalResult
from app.services.ai_service import run_ai_analysis
from app.services.blockchain_service import check_provenance
from app.services.fusion import fuse_results

router = APIRouter()


@router.post("/analyze", response_model=FinalResult)
async def analyze_media(req: AnalyzeRequest):
    content = storage.get_content(req.content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="content_id not found. Upload it first.")

    ai_result = run_ai_analysis(content["filepath"])
    provenance_result = check_provenance(req.content_id)

    analysis_id = storage.new_id("analysis")
    final = fuse_results(analysis_id, ai_result, provenance_result)

    storage.save_analysis(analysis_id, {
        "content_id": req.content_id,
        "ai_result": ai_result.model_dump(),
        "provenance_result": provenance_result.model_dump(),
        "final_result": final.model_dump(),
    })

    return final