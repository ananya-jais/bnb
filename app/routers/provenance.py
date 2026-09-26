from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException  # type: ignore[import-not-found]

from app import storage

from app.schemas import (
    ProvenanceRegisterRequest,
    ProvenanceVerifyRequest,
    ProvenanceResult,
)

from app.services.blockchain_service import check_provenance, contract, web3
router = APIRouter()


@router.post("/provenance/register")
async def register(req: ProvenanceRegisterRequest):
    content = storage.get_content(req.content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="content_id not found. Upload it first.")

    timestamp = datetime.now(timezone.utc).isoformat()
    storage.register_provenance(req.content_id, req.creator, req.signature, timestamp)
    tx_hash = contract.functions.registerContent(
        req.content_id,
        content["sha256"],
        content.get("perceptual_hash") or "",
        req.creator,
        "",
        "original"
    ).transact({
        "from": web3.eth.accounts[0]
    })

    return {"content_id": req.content_id, "registered": True, "timestamp": timestamp}


@router.post("/provenance/verify", response_model=ProvenanceResult)
async def verify(req: ProvenanceVerifyRequest):
    return check_provenance(req.content_id)


@router.get("/provenance/{content_id}")
async def get_history(content_id: str):
    record = storage.get_provenance(content_id)
    if record is None:
        raise HTTPException(status_code=404, detail="No provenance record for this content_id.")
    return record