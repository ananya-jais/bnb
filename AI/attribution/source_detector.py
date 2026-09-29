from pathlib import Path

import numpy as np
import onnxruntime as ort
from PIL import Image
from huggingface_hub import hf_hub_download


MODEL_REPO = "onnx-community/ai-source-detector-ONNX"
MODEL_FILE = "onnx/model_q4.onnx"

LABELS = [
    "stable_diffusion",
    "midjourney",
    "dalle",
    "real",
    "other_ai"
]


print("Downloading/loading source attribution model...")

model_path = hf_hub_download(
    repo_id=MODEL_REPO,
    filename=MODEL_FILE
)

session = ort.InferenceSession(
    model_path,
    providers=["CPUExecutionProvider"]
)

print("Source attribution model loaded!")


def detect_source(image_path):

    image = Image.open(image_path).convert("RGB")

    image = image.resize((224, 224))

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

    input_name = session.get_inputs()[0].name

    output = session.run(
        None,
        {input_name: image.astype(np.float32)}
    )

    logits = np.asarray(output[0]).reshape(-1)

    exp_values = np.exp(
        logits - np.max(logits)
    )

    probabilities = (
        exp_values / exp_values.sum()
    )

    results = []

    for label, probability in zip(
        LABELS,
        probabilities
    ):
        results.append({
            "label": label,
            "score": float(probability)
        })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results


if __name__ == "__main__":

    image_path = input(
        "\nEnter image path: "
    ).strip()

    if not Path(image_path).exists():

        print("\nImage not found!")

        exit()

    results = detect_source(image_path)

    print("\n================================")
    print("   VERITRACE SOURCE DETECTOR")
    print("================================")

    for result in results:

        print(
            f"{result['label']:20s} "
            f"{result['score'] * 100:.2f}%"
        )

    print("================================")