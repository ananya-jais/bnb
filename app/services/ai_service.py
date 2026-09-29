import logging
import os
import traceback

from app.schemas import AIResult

try:
    from AI.veritrace_detector import analyze_image as run_ml_analysis
    ML_MODEL_AVAILABLE = True
except Exception as e:
    logging.warning(f"Could not load AI/veritrace_detector.py model: {e}")
    ML_MODEL_AVAILABLE = False

_CLASS_MAP = {"REAL": "authentic", "SYNTHETIC": "synthetic"}
_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"}


def _to_unit(value) -> float:
    """Kanchan's pipeline reports 0-100; AIResult needs 0-1."""
    if value is None:
        return 0.0
    value = float(value)
    return value / 100.0 if value > 1.0 else value


def run_ai_analysis(file_path: str) -> AIResult:
    is_image = os.path.splitext(file_path)[1].lower() in _IMAGE_EXTS

    if ML_MODEL_AVAILABLE:
        try:
            ml_output = run_ml_analysis(file_path)

            raw_class = str(ml_output.get("classification", "REAL")).upper()
            classification = _CLASS_MAP.get(raw_class, "uncertain")
            confidence = _to_unit(ml_output.get("confidence", 0.0))

            if classification == "synthetic":
                synthetic_prob = confidence
            elif classification == "authentic":
                synthetic_prob = round(1.0 - confidence, 4)
            else:
                synthetic_prob = 0.5

            generation_family = ml_output.get("generation_family") or None
            evidence = list(ml_output.get("evidence", []))

            # Video/audio-only signals don't apply to a still image.
            if is_image:
                evidence = [e for e in evidence if "audio_video" not in e and "lip_sync" not in e]
                if generation_family == "lip_sync":
                    generation_family = None

            return AIResult(
                synthetic_probability=round(synthetic_prob, 4),
                classification=classification,
                generation_family=generation_family,
                confidence=round(confidence, 4),
                evidence=evidence,
                attribution_scores=ml_output.get("attribution_scores", {}),
                forensics=ml_output.get("forensics", {}),
            )

        except Exception as err:
            logging.error(f"Error executing AI ML pipeline: {err}")
            logging.error(traceback.format_exc())

    return AIResult(
        synthetic_probability=0.075,
        classification="authentic",
        generation_family=None,
        confidence=0.925,
        evidence=["Fallback engine: ML pipeline unavailable for this file."],
        attribution_scores={},
        forensics={},
    )


analyze_media_ai = run_ai_analysis