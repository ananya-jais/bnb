from transformers import pipeline
from pathlib import Path

print("Loading AI model...")

detector = pipeline(
    "image-classification",
    model="dima806/ai_vs_real_image_detection"
)

print("Model loaded!\n")

folders = {
    "REAL": Path("AI/samples/genuine"),
    "SYNTHETIC": Path("AI/samples/synthetic")
}

for actual_label, folder in folders.items():

    for image_path in folder.iterdir():

        if image_path.suffix.lower() not in [".jpg", ".jpeg", ".png", ".webp"]:
            continue

        result = detector(str(image_path))

        print("=" * 45)
        print(f"Image  : {image_path.name}")
        print(f"Actual : {actual_label}")
        print("AI prediction:")

        for item in result:
            print(f"  {item['label']} : {item['score'] * 100:.2f}%")