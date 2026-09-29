import cv2
import os
import tempfile
import numpy as np

from AI.veritrace_detector import detect_ai, THRESHOLD


# ==========================================
# VIDEO VISUAL DETECTOR
# ==========================================

def analyze_video_visual(video_path, sample_count=12):

    if not os.path.exists(video_path):
        raise FileNotFoundError(
            f"Video not found: {video_path}"
        )

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise RuntimeError(
            "Could not open video."
        )

    total_frames = int(
        cap.get(cv2.CAP_PROP_FRAME_COUNT)
    )

    fps = cap.get(
        cv2.CAP_PROP_FPS
    )

    if fps <= 0:
        fps = 25.0

    duration = total_frames / fps

    # --------------------------------------
    # Select evenly spaced frames
    # --------------------------------------

    frame_indices = np.linspace(
        0,
        max(total_frames - 1, 0),
        sample_count,
        dtype=int
    )

    logits = []
    frame_results = []

    # Temporary folder for frames
    temp_dir = tempfile.mkdtemp(
        prefix="veritrace_frames_"
    )

    try:

        for index in frame_indices:

            cap.set(
                cv2.CAP_PROP_POS_FRAMES,
                int(index)
            )

            success, frame = cap.read()

            if not success:
                continue

            frame_path = os.path.join(
                temp_dir,
                f"frame_{index}.jpg"
            )

            cv2.imwrite(
                frame_path,
                frame
            )

            classification, raw_logit, confidence = detect_ai(
                frame_path
            )

            logits.append(raw_logit)

            frame_results.append(
                {
                    "frame": int(index),
                    "time": round(
                        float(index / fps),
                        2
                    ),
                    "classification": classification,
                    "raw_logit": round(
                        float(raw_logit),
                        4
                    ),
                    "confidence": round(
                        float(confidence),
                        2
                    )
                }
            )

    finally:

        cap.release()

        # Remove temporary frames
        for filename in os.listdir(temp_dir):

            try:
                os.remove(
                    os.path.join(
                        temp_dir,
                        filename
                    )
                )

            except:
                pass

        try:
            os.rmdir(temp_dir)
        except:
            pass

    if not logits:

        raise RuntimeError(
            "No video frames could be analyzed."
        )

    logits = np.array(
        logits,
        dtype=np.float32
    )

    # --------------------------------------
    # Robust aggregation
    # --------------------------------------

    median_logit = float(
        np.median(logits)
    )

    high_percentile_logit = float(
        np.percentile(logits, 75)
    )

    suspicious_fraction = float(
        np.mean(logits >= 1.359375)
    )

    # --------------------------------------
    # Final visual decision
    # --------------------------------------
    #
    # We use the median rather than simple
    # frame majority voting.
    #
    # This avoids the previous problem where
    # both real and fake videos received the
    # same 7/12 synthetic-frame result.
    # --------------------------------------

    threshold = THRESHOLD

    if median_logit >= threshold:

        classification = "suspicious"

        signal_strength = min(
            1.0,
            max(
                0.0,
                (median_logit - threshold) / 4.0
            )
        )

        evidence = (
            "Sampled video frames show "
            "AI-generation/manipulation indicators."
        )

    else:

        classification = "no_strong_visual_signal"

        signal_strength = min(
            1.0,
            max(
                0.0,
                (threshold - median_logit) / 4.0
            )
        )

        evidence = (
            "Sampled video frames do not show "
            "a strong AI-generation signal."
        )

    return {

        "classification": classification,

        "signal_strength": round(
            signal_strength,
            4
        ),

        "median_logit": round(
            median_logit,
            4
        ),

        "high_percentile_logit": round(
            high_percentile_logit,
            4
        ),

        "suspicious_frame_fraction": round(
            suspicious_fraction,
            4
        ),

        "frames_analyzed": len(
            frame_results
        ),

        "video_duration_seconds": round(
            duration,
            2
        ),

        "evidence": evidence,

        "frame_results": frame_results
    }