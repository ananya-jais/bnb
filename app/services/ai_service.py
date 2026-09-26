"""
Kanchan's module lives here. Keep the function signature and the
AIResult shape (see app/schemas.py) stable — that's the whole
integration contract with the backend.
"""

import random
from app.schemas import AIResult


def run_ai_analysis(filepath: str) -> AIResult:
    # TODO(Kanchan): replace with real frame/audio/cross-modal analysis.
    synthetic_probability = round(random.uniform(0.0, 1.0), 2)
    is_synthetic = synthetic_probability > 0.5

    return AIResult(
        synthetic_probability=synthetic_probability,
        classification="synthetic" if is_synthetic else "authentic",
        generation_family="lip_sync" if is_synthetic else None,
        confidence=round(random.uniform(0.7, 0.95), 2),
        evidence=["audio_video_mismatch"] if is_synthetic else ["no_manipulation_artifacts_detected"],
    )