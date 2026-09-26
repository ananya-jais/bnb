"""
VeriTrace AI analysis service.

This module connects the backend to Kanchan's image AI detector.
The AIResult structure must remain unchanged because it is the
integration contract with the rest of the backend.
"""

from app.schemas import AIResult
from AI.veritrace_detector import analyze_image


def run_ai_analysis(filepath: str) -> AIResult:
    """
    Analyze an uploaded image using the VeriTrace AI detector.
    """

    # Run the real AI detector
    result = analyze_image(filepath)

    # Convert detector confidence (%) into the backend's 0-1 format
    confidence = result["confidence"] / 100.0

    # Convert REAL/SYNTHETIC into backend terminology
    if result["classification"] == "SYNTHETIC":
        classification = "synthetic"
        synthetic_probability = confidence
        generation_family = result.get("generation_family")

    else:
        classification = "authentic"
        synthetic_probability = 1.0 - confidence
        generation_family = None

    # Keep only useful user-facing evidence
    evidence = []

    if classification == "synthetic":
        evidence.append("AI-generation patterns detected in the image.")
    else:
        evidence.append("No strong AI-generation patterns detected.")

    evidence.append("Additional forensic image analysis completed.")

    return AIResult(
        synthetic_probability=round(synthetic_probability, 4),
        classification=classification,
        generation_family=generation_family,
        confidence=round(confidence, 4),
        evidence=evidence,
    )