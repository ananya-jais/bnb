"""
This is your core deliverable: combine AI + provenance into one
verdict. Implements the three mandatory demo scenarios from the plan.
"""

from app.schemas import AIResult, ProvenanceResult, FinalResult


def fuse_results(analysis_id: str, ai: AIResult, prov: ProvenanceResult) -> FinalResult:
    evidence = list(ai.evidence)

    is_likely_synthetic = ai.classification == "synthetic" and ai.synthetic_probability >= 0.5

    if is_likely_synthetic and not prov.provenance_found:
        status = "SUSPICIOUS_UNVERIFIED"
        if "no_provenance_record" not in evidence:
            evidence.append("no_provenance_record")

    elif not is_likely_synthetic and prov.provenance_found and prov.edit_type in (None, "none"):
        status = "VERIFIED_ORIGINAL"

    elif not is_likely_synthetic and prov.provenance_found and prov.edit_type not in (None, "none"):
        status = "EDITED_PROVENANCE_VERIFIED"
        evidence.append(f"known_edit:{prov.edit_type}")

    else:
        status = "UNCERTAIN"

    return FinalResult(
        analysis_id=analysis_id,
        status=status,
        synthetic_probability=ai.synthetic_probability,
        generation_family=ai.generation_family,
        provenance_found=prov.provenance_found,
        blockchain_verified=prov.blockchain_verified,
        confidence=ai.confidence,
        evidence=evidence,
    )