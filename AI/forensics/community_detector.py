from pathlib import Path

import numpy as np
from PIL import Image
import onnxruntime as ort
from huggingface_hub import hf_hub_download


MODEL_REPO = "Thermostatic/community-forensics-frontier-detector-2026-08"
MODEL_FILE = "community_forensics_frontier_fp16.onnx"

THRESHOLD = 1.359375


def load_model():

    print("Downloading/loading Community Forensics model...")

    model_path = hf_hub_download(
        repo_id=MODEL_REPO,
        filename=MODEL_FILE
    )

    session = ort.InferenceSession(
        model_path,
        providers=["CPUExecutionProvider"]
    )

    print("Model loaded!")

    return session


def preprocess_image(image_path):

    image = Image.open(image_path).convert("RGB")

    width, height = image.size

    # Resize short edge to 440
    scale = 440 / min(width, height)

    new_width = int(width * scale)
    new_height = int(height * scale)

    image = image.resize(
        (new_width, new_height),
        Image.Resampling.BILINEAR
    )

    # Center crop 384 x 384
    left = (new_width - 384) // 2
    top = (new_height - 384) // 2

    image = image.crop(
        (left, top, left + 384, top + 384)
    )

    image = np.asarray(image).astype(np.float32) / 255.0

    # ImageNet normalization
    mean = np.array(
        [0.485, 0.456, 0.406],
        dtype=np.float32
    )

    std = np.array(
        [0.229, 0.224, 0.225],
        dtype=np.float32
    )

    image = (image - mean) / std

    # HWC -> CHW
    image = np.transpose(image, (2, 0, 1))

    # Add batch dimension
    image = np.expand_dims(image, axis=0)

    return image.astype(np.float32)


def analyze_image(session, image_path):

    image = preprocess_image(image_path)

    input_name = session.get_inputs()[0].name

    output = session.run(
        None,
        {input_name: image}
    )

    raw_logit = float(np.asarray(output[0]).reshape(-1)[0])

    if raw_logit >= THRESHOLD:
        classification = "SYNTHETIC"
    else:
        classification = "REAL"

    return classification, raw_logit


if __name__ == "__main__":

    folders = {
        "REAL": Path("AI/samples/genuine"),
        "SYNTHETIC": Path("AI/samples/synthetic")
    }

    session = load_model()

    correct = 0
    total = 0

    print("\n================================")
    print(" COMMUNITY FORENSICS TEST")
    print("================================")

    for actual_label, folder in folders.items():

        for image_path in folder.iterdir():

            if image_path.suffix.lower() not in [
                ".jpg", ".jpeg", ".png", ".webp"
            ]:
                continue

            classification, raw_logit = analyze_image(
                session,
                str(image_path)
            )

            total += 1

            predicted_correctly = (
                (actual_label == "REAL" and classification == "REAL")
                or
                (actual_label == "SYNTHETIC" and classification == "SYNTHETIC")
            )

            if predicted_correctly:
                correct += 1

            print(
                f"{image_path.name:20} "
                f"Actual: {actual_label:9} "
                f"Prediction: {classification:9} "
                f"Logit: {raw_logit:.4f}"
            )

    accuracy = (correct / total) * 100

    print("\n================================")
    print("RESULT")
    print("================================")
    print(f"Correct : {correct}/{total}")
    print(f"Accuracy: {accuracy:.2f}%")
    print("================================")