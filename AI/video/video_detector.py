import cv2
import tempfile
import os

from AI.veritrace_detector import analyze_image


def extract_frames(video_path, max_frames=12):
    """
    Extract evenly spaced frames from a video.

    Args:
        video_path: Path to the video file.
        max_frames: Maximum number of frames to extract.

    Returns:
        List of extracted video frames.
    """

    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"Could not open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if total_frames <= 0:
        cap.release()
        raise ValueError("Could not determine video frame count.")

    frame_indices = [
        int(i * (total_frames - 1) / max_frames)
        for i in range(max_frames)
    ]

    frames = []

    for index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, index)

        success, frame = cap.read()

        if success:
            frames.append(frame)

    cap.release()

    return frames


def analyze_video(video_path, max_frames=12):
    """
    Analyze a video by sampling frames and running
    the VeriTrace image detector on each frame.
    """

    frames = extract_frames(video_path, max_frames)

    if not frames:
        raise ValueError("No frames could be extracted from the video.")

    results = []

    for frame in frames:
        temp_path = None

        try:
            # Create temporary JPEG file for the image detector
            with tempfile.NamedTemporaryFile(
                suffix=".jpg",
                delete=False
            ) as temp_file:
                temp_path = temp_file.name

            # Save video frame as an image
            success = cv2.imwrite(temp_path, frame)

            if not success:
                continue

            # Run existing VeriTrace image detector
            result = analyze_image(temp_path)

            results.append(result)

        finally:
            # Delete temporary frame
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

    if not results:
        raise ValueError("Could not analyze any video frames.")

    # Count how many frames were classified as synthetic
    synthetic_count = sum(
        1
        for result in results
        if result["classification"] == "SYNTHETIC"
    )

    # Calculate proportion of synthetic frames
    synthetic_probability = synthetic_count / len(results)

    # Overall video classification
    if synthetic_probability >= 0.5:
        classification = "SYNTHETIC"
    else:
        classification = "REAL"

    # Confidence based on majority decision
    confidence = max(
        synthetic_probability,
        1 - synthetic_probability
    )

    return {
        "classification": classification,
        "synthetic_probability": round(synthetic_probability, 4),
        "confidence": round(confidence, 4),
        "frames_analyzed": len(results),
        "frame_results": results,
    }