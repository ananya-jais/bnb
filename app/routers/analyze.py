from fastapi import APIRouter, HTTPException

from app import storage
from app.schemas import AnalyzeRequest, FinalResult
from app.services.ai_service import run_ai_analysis
from app.services.blockchain_service import check_provenance, add_edit_on_chain
from app.services.phash_service import hamming_distance, MATCH_THRESHOLD
from app.services.fusion import fuse_results

router = APIRouter()


def _find_exact_match(content_id: str, sha256: str):
    """Same file, byte-for-byte — already registered under a different content_id."""
    candidate_ids = [content_id] + [
        c for c in storage.find_content_ids_by_sha256(sha256) if c != content_id
    ]
    for cid in candidate_ids:
        prov = check_provenance(cid)
        if prov.provenance_found:
            return cid, prov
    return None, None


def _find_edited_parent(content_id: str, perceptual_hash: str):
    """Different bytes, visually similar — look for a registered parent and auto-link it."""
    if not perceptual_hash:
        return None, None

    candidates = storage.get_all_content_with_phash(exclude_id=content_id)
    scored = []
    for c in candidates:
        try:
            dist = hamming_distance(perceptual_hash, c["perceptual_hash"])
        except Exception:
            continue
        scored.append((dist, c["content_id"]))
    scored.sort(key=lambda x: x[0])

    for dist, cid in scored:
        if dist > MATCH_THRESHOLD:
            break
        prov = check_provenance(cid)
        if prov.provenance_found:
            return cid, dist
    return None, None


@router.post("/analyze", response_model=FinalResult)
def analyze_media(req: AnalyzeRequest):
    content = storage.get_content(req.content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="content_id not found. Upload it first.")

    ai_result = run_ai_analysis(content["filepath"])

    # 1. Exact re-upload of an already-registered file.
    matched_id, provenance_result = _find_exact_match(req.content_id, content["sha256"])

    # 2. Not an exact match — check for a visually similar registered parent.
    if provenance_result is None:
        parent_id, distance = _find_edited_parent(req.content_id, content["perceptual_hash"])
        if parent_id:
            try:
                add_edit_on_chain(
                    req.content_id,
                    content["sha256"],
                    content["perceptual_hash"],
                    "auto-detected",
                    parent_id,
                    "auto_detected_edit",
                )
                matched_id = req.content_id
                provenance_result = check_provenance(req.content_id)
            except Exception:
                provenance_result = check_provenance(req.content_id)  # falls through to not-found
        else:
            provenance_result = check_provenance(req.content_id)

    analysis_id = storage.new_id("analysis")
    final = fuse_results(analysis_id, ai_result, provenance_result)
    final.matched_content_id = matched_id

    storage.save_analysis(analysis_id, {
        "content_id": req.content_id,
        "ai_result": ai_result.model_dump(),
        "provenance_result": provenance_result.model_dump(),
        "final_result": final.model_dump(),
    })

    return final