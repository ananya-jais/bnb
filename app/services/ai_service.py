"""
VeriTrace AI analysis service.

Images use the existing image detector.
Videos use the visual + audio + AuViRe fusion pipeline.

The shared AIResult schema remains unchanged.
"""

import os

from app.schemas import AIResult

# Existing image detector
from AI.veritrace_detector import analyze_image


# =========================================================
# IMAGE ANALYSIS
# =========================================================

def run_image_analysis(filepath: str) -> AIResult:
    """
    Analyze an uploaded image using the existing
    VeriTrace image detector.

    This is the existing image logic.
    """

    result = analyze_image(filepath)

    # Convert detector confidence (%) into backend 0-1 format
    confidence = result["confidence"] / 100.0

    if result["classification"] == "SYNTHETIC":
        classification = "synthetic"
        synthetic_probability = confidence
        generation_family = result.get("generation_family")

    else:
        classification = "authentic"
        synthetic_probability = 1.0 - confidence
        generation_family = None

    evidence = []

    if classification == "synthetic":
        evidence.append(
            "AI-generation patterns detected in the image."
        )
    else:
        evidence.append(
            "No strong AI-generation patterns detected."
        )

    evidence.append(
        "Additional forensic image analysis completed."
    )

    return AIResult(
        synthetic_probability=round(
            synthetic_probability,
            4
        ),
        classification=classification,
        generation_family=generation_family,
        confidence=round(
            confidence,
            4
        ),
        evidence=evidence,
    )


# =========================================================
# VIDEO ANALYSIS
# =========================================================

def run_video_analysis(filepath: str) -> AIResult:
    """
    Analyze an uploaded video using:

    1. Visual detector
    2. Audio detector
    3. AuViRe audio-visual detector
    4. Video evidence fusion
    """
    
    filepath = os.path.abspath(filepath)
    from AI.video.visual_detector import analyze_video_visual
    from AI.video.audio.audio_detector import analyze_audio
    from AI.video.video_fusion import fuse_video_results

    # AuViRe is installed in the separate AuViRe environment.
    from src.itw import run_auvire

    # -----------------------------------------------------
    # Run visual analysis
    # -----------------------------------------------------

    visual_result = analyze_video_visual(filepath)

    # -----------------------------------------------------
    # Run audio analysis
    # -----------------------------------------------------

    audio_result = analyze_audio(filepath)

 
    # -----------------------------------------------------
    # Run AuViRe
    # -----------------------------------------------------

    # AuViRe expects its checkpoint/config paths
    # relative to the AuViRe project directory.
    original_cwd = os.getcwd()

    try:
        os.chdir(r"C:\Users\Kanchan\auvire")

        auvire_result = run_auvire(
            model_training_dataset="lavdf",
            video_path=filepath,
            return_landmarks=False,
            device="cpu",
            core_response=False,
        )

    finally:
        os.chdir(original_cwd)
 

    # -----------------------------------------------------
    # Fuse all three branches
    # -----------------------------------------------------

    fused_result = fuse_video_results(
        visual_result,
        audio_result,
        auvire_result,
    )

    classification_text = fused_result[
        "classification"
    ]

    evidence_score = float(
        fused_result.get(
            "evidence_score",
            0.0
        )
    )

    evidence_strength = fused_result.get(
        "evidence_strength",
        "Low"
    )

    # -----------------------------------------------------
    # Convert fusion result into shared AIResult
    # -----------------------------------------------------

    if classification_text == "Likely Synthetic":

        classification = "synthetic"

        synthetic_probability = evidence_score

        confidence = evidence_score

    elif classification_text == "Likely Real":

        classification = "authentic"

        synthetic_probability = (
            1.0 - evidence_score
        )

        confidence = evidence_score

    else:

        classification = "uncertain"

        synthetic_probability = evidence_score

        # Uncertain result gets a lower confidence score
        # when the evidence is close to the middle.
        confidence = (
            1.0
            - abs(evidence_score - 0.5) * 2
        )

    # -----------------------------------------------------
    # Build evidence list
    # -----------------------------------------------------

    evidence = []

    # -------------------------
    # Visual evidence
    # -------------------------

    visual = fused_result[
        "branches"
    ].get(
        "visual",
        {}
    )

    if visual.get(
        "classification"
    ) == "suspicious":

        suspicious_fraction = float(
            visual.get(
                "suspicious_frame_fraction",
                0.0
            )
        )

        evidence.append(
            "Visual analysis detected suspicious "
            "AI-generation indicators in "
            f"{suspicious_fraction * 100:.1f}% "
            "of sampled frames."
        )

    else:

        evidence.append(
            "Visual analysis detected no strong "
            "AI-generation signal in the sampled frames."
        )

    # -------------------------
    # Audio evidence
    # -------------------------

    audio = fused_result[
        "branches"
    ].get(
        "audio",
        {}
    )

    if audio.get(
        "classification"
    ) == "suspicious":

        spoof_score = float(
            audio.get(
                "spoof_score",
                0.0
            )
        )

        evidence.append(
            "Audio analysis detected a strong "
            "spoof/synthetic-speech signal "
            f"(model score: {spoof_score:.4f})."
        )

    else:

        evidence.append(
            "Audio analysis detected no strong "
            "spoof signal."
        )

    # -------------------------
    # Audio-visual evidence
    # -------------------------

    audio_visual = fused_result[
        "branches"
    ].get(
        "audio_visual",
        {}
    )

    if (
        audio_visual.get(
            "score_prob_threshold"
        ) is not None
    ):

        auvire_score = float(
            audio_visual[
                "score_prob_threshold"
            ]
        )

        if auvire_score >= 20:

            evidence.append(
                "Audio-visual analysis detected "
                "suspicious activity."
            )

            suspicious_intervals = (
                fused_result[
                    "summary"
                ][
                    "audio_visual_analysis"
                ].get(
                    "suspicious_intervals",
                    []
                )
            )

            for interval in suspicious_intervals:

                evidence.append(
                    "Suspicious audio-visual interval: "
                    f"{interval['start']:.2f}s - "
                    f"{interval['end']:.2f}s."
                )

        else:

            evidence.append(
                "No strong audio-visual "
                "manipulation signal was detected."
            )

    else:

        evidence.append(
            "Audio-visual analysis was not applicable "
            "because no valid visible-speech segment "
            "was available."
        )

    # -------------------------
    # Overall strength
    # -------------------------

    evidence.append(
        "Overall video evidence strength: "
        f"{evidence_strength}."
    )

    # -----------------------------------------------------
    # Final shared AIResult
    # -----------------------------------------------------

    return AIResult(

        synthetic_probability=round(
            max(
                0.0,
                min(
                    1.0,
                    synthetic_probability
                )
            ),
            4
        ),

        classification=classification,

        generation_family=(
            "Multimodal video analysis"
        ),

        confidence=round(
            max(
                0.0,
                min(
                    1.0,
                    confidence
                )
            ),
            4
        ),

        evidence=evidence,
    )


# =========================================================
# MAIN DISPATCHER
# =========================================================

def run_ai_analysis(filepath: str) -> AIResult:
    """
    Automatically select image or video analysis
    based on file extension.
    """

    extension = os.path.splitext(
        filepath
    )[1].lower()

    image_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".bmp",
        ".tiff",
        ".tif",
    }

    video_extensions = {
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
        ".m4v",
    }

    if extension in image_extensions:

        return run_image_analysis(
            filepath
        )

    if extension in video_extensions:

        return run_video_analysis(
            filepath
        )

    raise ValueError(
        f"Unsupported media type: {extension}"
    )