from app.schemas import AIResult, ProvenanceResult, FinalResult

LOW_RISK_THRESHOLD = 0.30  # below this, call it "likely authentic" even unregistered


def fuse_results(analysis_id: str, ai: AIResult, prov: ProvenanceResult) -> FinalResult:
    evidence = list(ai.evidence)
    prob = ai.synthetic_probability
    is_likely_synthetic = ai.classification == "synthetic" and prob >= 0.5

    if is_likely_synthetic and not prov.provenance_found:
        status = "SUSPICIOUS_UNVERIFIED"
        if "no_provenance_record" not in evidence:
            evidence.append("no_provenance_record")

    elif prov.provenance_found and prov.edit_type in (None, "none") and not is_likely_synthetic:
        status = "VERIFIED_ORIGINAL"

    elif prov.provenance_found and prov.edit_type not in (None, "none") and not is_likely_synthetic:
        status = "EDITED_PROVENANCE_VERIFIED"
        evidence.append(f"known_edit:{prov.edit_type}")

    elif not prov.provenance_found and not is_likely_synthetic and prob < LOW_RISK_THRESHOLD:
        # Low synthetic score, nothing suspicious, just never registered.
        status = "LIKELY_AUTHENTIC_UNREGISTERED"
        if "no_provenance_record" not in evidence:
            evidence.append("no_provenance_record")

    else:
        status = "UNCERTAIN"

    return FinalResult(
        analysis_id=analysis_id,
        status=status,
        synthetic_probability=prob,
        generation_family=ai.generation_family,
        provenance_found=prov.provenance_found,
        blockchain_verified=prov.blockchain_verified,
        confidence=ai.confidence,
        evidence=evidence,
        attribution_scores=ai.attribution_scores,
        forensics=ai.forensics,
    )