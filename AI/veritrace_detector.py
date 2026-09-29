import json
from pathlib import Path

from PIL import Image
import numpy as np
import onnxruntime as ort
from huggingface_hub import hf_hub_download

from AI.attribution.source_detector import detect_source


# ==========================================
# COMMUNITY FORENSICS MODEL
# ==========================================

MODEL_REPO = "Thermostatic/community-forensics-frontier-detector-2026-08"
MODEL_FILE = "community_forensics_frontier_fp16.onnx"

THRESHOLD = 1.359375


print("Loading VeriTrace AI detector...")

model_path = hf_hub_download(
    repo_id=MODEL_REPO,
    filename=MODEL_FILE
)

session = ort.InferenceSession(
    model_path,
    providers=["CPUExecutionProvider"]
)

print("VeriTrace AI detector loaded!")


# ==========================================
# IMAGE PREPROCESSING
# ==========================================

def preprocess_image(image_path):

    image = Image.open(image_path).convert("RGB")

    width, height = image.size

    scale = 440 / min(width, height)

    new_width = int(width * scale)
    new_height = int(height * scale)

    image = image.resize(
        (new_width, new_height),
        Image.Resampling.BILINEAR
    )

    left = (new_width - 384) // 2
    top = (new_height - 384) // 2

    image = image.crop(
        (left, top, left + 384, top + 384)
    )

    image = np.asarray(image).astype(np.float32) / 255.0

    mean = np.array(
        [0.485, 0.456, 0.406],
        dtype=np.float32
    )

    std = np.array(
        [0.229, 0.224, 0.225],
        dtype=np.float32
    )

    image = (image - mean) / std

    image = np.transpose(image, (2, 0, 1))

    image = np.expand_dims(image, axis=0)

    return image.astype(np.float32)


# ==========================================
# FORENSIC ANALYSIS
# ==========================================

def analyze_forensics(image_path):

    image = Image.open(image_path).convert("RGB")

    image_array = np.array(image)

    height, width = image_array.shape[:2]

    gray = np.mean(image_array, axis=2)

    brightness = image_array.mean()

    contrast = image_array.std()

    horizontal_edges = np.abs(
        np.diff(gray, axis=1)
    ).mean()

    vertical_edges = np.abs(
        np.diff(gray, axis=0)
    ).mean()

    edge_strength = (
        horizontal_edges + vertical_edges
    ) / 2

    fft = np.fft.fft2(gray)

    fft_shift = np.fft.fftshift(fft)

    magnitude = np.abs(fft_shift)

    frequency_energy = np.mean(
        np.log1p(magnitude)
    )

    y_start = int(height * 0.25)
    y_end = int(height * 0.75)

    x_start = int(width * 0.25)
    x_end = int(width * 0.75)

    high_frequency_energy = np.mean(
        magnitude[
            y_start:y_end,
            x_start:x_end
        ]
    )

    return {
        "width": width,
        "height": height,
        "brightness": round(float(brightness), 2),
        "contrast": round(float(contrast), 2),
        "edge_strength": round(float(edge_strength), 2),
        "frequency_energy": round(float(frequency_energy), 2),
        "high_frequency_energy": round(
            float(high_frequency_energy), 2
        )
    }


# ==========================================
# AI DETECTION
# ==========================================

def detect_ai(image_path):

    image = preprocess_image(image_path)

    input_name = session.get_inputs()[0].name

    output = session.run(
        None,
        {input_name: image}
    )

    raw_logit = float(
        np.asarray(output[0]).reshape(-1)[0]
    )

    # Convert detector score into a
    # confidence-like percentage.
    confidence_value = 1 / (
        1 + np.exp(-(raw_logit - THRESHOLD))
    )

    if raw_logit >= THRESHOLD:

        classification = "SYNTHETIC"

        confidence = confidence_value * 100

    else:

        classification = "REAL"

        confidence = (1 - confidence_value) * 100

    return classification, raw_logit, confidence


# ==========================================
# MAIN VERITRACE FUNCTION
# ==========================================

def analyze_image(image_path):

    # AI detection
    classification, raw_logit, confidence = detect_ai(
        image_path
    )

    # Generation/source attribution
    attribution_results = detect_source(
        image_path
    )

    # Forensic analysis
    forensic_data = analyze_forensics(
        image_path
    )

    # ======================================
    # EVIDENCE
    # ======================================

    evidence = []

    if classification == "SYNTHETIC":

        evidence.append(
            "AI-generation detector classified "
            "the image as synthetic."
        )

    else:

        evidence.append(
            "AI-generation detector classified "
            "the image as real."
        )

    evidence.append(
        f"Detector logit: {raw_logit:.4f}"
    )

    evidence.append(
        f"Decision threshold: {THRESHOLD}"
    )

    evidence.append(
        "Additional forensic image analysis completed."
    )

    # ======================================
    # ATTRIBUTION SCORES
    # ======================================

    attribution_scores = {}

    for item in attribution_results:

        attribution_scores[item["label"]] = round(
            item["score"] * 100,
            2
        )

    # ======================================
    # GENERATION FAMILY
    # ======================================

    generation_family = "Uncertain"

    # We do NOT automatically claim a specific
    # generator because our testing showed that
    # the attribution model can confuse real
    # images with AI-source categories.

    # Only provide attribution information when
    # the main detector says SYNTHETIC.

    if classification == "SYNTHETIC":

        generation_family = "Uncertain"

    else:

        generation_family = "Not applicable"


    # ======================================
    # FINAL RESULT
    # ======================================

    result = {

        "classification": classification,

        "confidence": round(
            confidence,
            2
        ),

        "generation_family": generation_family,

        "attribution_scores": attribution_scores,

        "evidence": evidence,

        "forensics": forensic_data
    }

    return result


# ==========================================
# TEST MODE
# ==========================================

if __name__ == "__main__":

    image_path = input(
        "\nEnter image path: "
    ).strip()

    if not Path(image_path).exists():

        print("\nImage not found!")

        exit()

    result = analyze_image(
        image_path
    )

    print("\n================================")
    print("       VERITRACE AI")
    print("================================")

    print(
        json.dumps(
            result,
            indent=4
        )
    )

    print("================================")