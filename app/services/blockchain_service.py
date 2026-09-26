"""
Vidhi's module lives here. Keep the function signature and the
ProvenanceResult shape (see app/schemas.py) stable.
"""

from app import storage
from app.schemas import ProvenanceResult


def check_provenance(content_id: str) -> ProvenanceResult:
    # TODO(Vidhi): replace with real on-chain hash/signature lookup.
    record = storage.get_provenance(content_id)

    if record is None:
        return ProvenanceResult(
            provenance_found=False,
            blockchain_verified=False,
        )

    return ProvenanceResult(
        provenance_found=True,
        original_content_id=content_id,
        creator=record.get("creator"),
        timestamp=record.get("timestamp"),
        edit_type=record["parent_chain"][-1]["edit_type"] if record.get("parent_chain") else "none",
        blockchain_verified=record.get("creator") is not None,
        parent_chain=[p["parent"] for p in record.get("parent_chain", [])],
    )