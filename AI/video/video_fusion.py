def fuse_video_results(visual, audio, auvire):
    """
    Combine visual, audio, and audio-visual evidence.

    Model scores are treated as evidence signals,
    not calibrated probabilities.
    """

    # ==========================================
    # INDIVIDUAL BRANCH SCORES
    # ==========================================

    visual_score = float(
        visual.get("signal_strength", 0.0)
    )

    audio_score = float(
        audio.get("spoof_score", 0.0)
    )

    auvire_threshold = auvire.get(
        "score_prob_threshold"
    )

    if auvire_threshold is None:
        auvire_score = 0.0
    else:
        auvire_score = float(
            auvire_threshold
        ) / 100.0

    # ==========================================
    # SUSPICIOUS BRANCHES
    # ==========================================

    suspicious_branches = 0

    if visual.get("classification") == "suspicious":
        suspicious_branches += 1

    if audio.get("classification") == "suspicious":
        suspicious_branches += 1

    if auvire_score >= 0.20:
        suspicious_branches += 1

    # ==========================================
    # COMBINED EVIDENCE SCORE
    # ==========================================

    combined_score = (
        0.35 * visual_score
        + 0.35 * audio_score
        + 0.30 * auvire_score
    )

    # ==========================================
    # FINAL CLASSIFICATION
    # ==========================================

    if (
        suspicious_branches >= 2
        and combined_score >= 0.50
    ):

        classification = "Likely Synthetic"

    elif (
        suspicious_branches == 0
        and combined_score < 0.35
    ):

        classification = "Likely Real"

    else:

        classification = "Uncertain"

    # ==========================================
    # EVIDENCE STRENGTH
    # ==========================================

    if suspicious_branches >= 3:

        evidence_strength = "High"

    elif suspicious_branches == 2:

        evidence_strength = "Moderate"

    elif suspicious_branches == 1:

        evidence_strength = "Mixed"

    else:

        evidence_strength = "Low"

    # ==========================================
    # VISUAL SUMMARY
    # ==========================================

    if visual.get("classification") == "suspicious":

        suspicious_fraction = (
            visual.get(
                "suspicious_frame_fraction",
                0.0
            ) * 100
        )

        visual_summary = (
            "Synthetic indicators detected in "
            f"{suspicious_fraction:.1f}% of sampled frames."
        )

    else:

        visual_summary = (
            "No strong AI-generation signal "
            "detected in sampled frames."
        )

    # ==========================================
    # AUDIO SUMMARY
    # ==========================================

    if audio.get("classification") == "suspicious":

        audio_summary = (
            "Suspicious synthetic-speech signal detected."
        )

    else:

        audio_summary = (
            "No strong synthetic-speech signal detected."
        )

    # ==========================================
    # AUVIRE SUMMARY
    # ==========================================

    segments = auvire.get("segments") or []

    valid_segments = [
        segment
        for segment in segments
        if segment.get("valid") is True
    ]

    if auvire_score >= 0.20:

        auvire_summary = (
            "Suspicious audio-visual activity detected."
        )

    elif not valid_segments:

        auvire_summary = (
            "Audio-visual analysis was not applicable "
            "because no valid visible-speech segment "
            "was available."
        )

    else:

        auvire_summary = (
            "No strong audio-visual mismatch signal detected."
        )

    # ==========================================
    # SUSPICIOUS INTERVALS
    # ==========================================

    suspicious_intervals = []

    for segment in (
        auvire.get("fake_period_scores") or []
    ):


        score = segment.get(
            "score"
        )

        if score is None:
            continue

        if score >= 0.20:

            suspicious_intervals.append(
                {
                    "start": round(
                        float(
                            segment.get(
                                "start",
                                0.0
                            )
                        ),
                        2
                    ),
                    "end": round(
                        float(
                            segment.get(
                                "end",
                                0.0
                            )
                        ),
                        2
                    ),
                    "score": round(
                        float(score),
                        4
                    )
                }
            )

    # ==========================================
    # HUMAN-READABLE RESULT
    # ==========================================

    summary = {

        "classification": classification,

        "evidence_strength": evidence_strength,

        "visual_analysis": {
            "status": (
                "Suspicious"
                if visual.get("classification")
                == "suspicious"
                else "No strong signal"
            ),
            "summary": visual_summary
        },

        "audio_analysis": {
            "status": (
                "Suspicious"
                if audio.get("classification")
                == "suspicious"
                else "No strong signal"
            ),
            "summary": audio_summary
        },

        "audio_visual_analysis": {
            "status": (
                "Suspicious"
                if auvire_score >= 0.20
                else (
                    "Not applicable"
                    if not valid_segments
                    else "No strong signal"
                )
            ),
            "summary": auvire_summary,
            "suspicious_intervals": suspicious_intervals
        },

        "overall_assessment": (
            "Multiple independent analysis branches "
            "reported suspicious signals."
            if suspicious_branches >= 2
            else (
                "The available signals are mixed."
                if suspicious_branches == 1
                else
                "No strong suspicious signals were detected."
            )
        )
    }

    # ==========================================
    # FINAL API RESULT
    # ==========================================

    return {

        "classification": classification,

        # Keep the numerical score internally.
        # It is NOT a calibrated probability.
        "evidence_score": round(
            combined_score,
            4
        ),

        "evidence_strength": evidence_strength,

        "suspicious_branches": suspicious_branches,

        "summary": summary,

        # Keep original technical outputs
        # for debugging and transparency.
        "branches": {

            "visual": visual,

            "audio": audio,

            "audio_visual": auvire

        }

    }