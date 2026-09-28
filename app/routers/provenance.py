from fastapi import APIRouter, HTTPException
from app import storage
from app.schemas import (
    ProvenanceRegisterRequest,
    ProvenanceEditRequest,
    ProvenanceVerifyRequest,
    ProvenanceResult,
)
from app.services import blockchain_service as chain

router = APIRouter()

def _content_or_404(content_id: str) -> dict:
    content = storage.get_content(content_id)
    if content is None:
        raise HTTPException(status_code=404, detail=f"content_id '{content_id}' not found. Upload it first.")
    return content

def _require_chain():
    if not chain.is_chain_up() or not chain.contract_deployed():
        raise HTTPException(
            status_code=503,
            detail="Blockchain node unreachable or contract not deployed. Start `npx hardhat node` and redeploy the contract.",
        )

@router.post("/provenance/register")
async def register(req: ProvenanceRegisterRequest):
    content = _content_or_404(req.content_id)
    _require_chain()
    try:
        tx = chain.register_on_chain(req.content_id, content["sha256"], content["perceptual_hash"], req.creator)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Chain rejected registration: {e}")
    return {"content_id": req.content_id, "registered": True, "tx_hash": tx}

@router.post("/provenance/edit")
async def register_edit(req: ProvenanceEditRequest):
    content = _content_or_404(req.content_id)
    _require_chain()
    try:
        tx = chain.add_edit_on_chain(
            req.content_id,
            content["sha256"],
            content["perceptual_hash"],
            req.creator,
            req.parent_id,
            req.edit_type,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Chain rejected edit: {e}")
    return {
        "content_id": req.content_id,
        "parent_id": req.parent_id,
        "edit_type": req.edit_type,
        "tx_hash": tx,
    }

@router.post("/provenance/verify", response_model=ProvenanceResult)
async def verify(req: ProvenanceVerifyRequest):
    _content_or_404(req.content_id)
    _require_chain()
    return chain.check_provenance(req.content_id)

@router.get("/provenance/{content_id}")
async def get_history(content_id: str):
    _require_chain()
    try:
        history = chain.get_history(content_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"No provenance found: {e}")
    if not history:
        raise HTTPException(status_code=404, detail="No provenance record for this content_id.")
    return {"content_id": content_id, "history": history}