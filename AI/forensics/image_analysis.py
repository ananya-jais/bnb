from PIL import Image
import numpy as np


def analyze_image(image_path):

    # Load image
    image = Image.open(image_path).convert("RGB")
    image_array = np.array(image)

    # Image dimensions
    height, width = image_array.shape[:2]

    # Convert RGB to grayscale
    gray = np.mean(image_array, axis=2)

    # Basic image statistics
    brightness = image_array.mean()
    contrast = image_array.std()

    # Edge analysis
    horizontal_edges = np.abs(np.diff(gray, axis=1)).mean()
    vertical_edges = np.abs(np.diff(gray, axis=0)).mean()

    edge_strength = (horizontal_edges + vertical_edges) / 2

    # ==========================================
    # FREQUENCY ANALYSIS USING FFT
    # ==========================================

    fft = np.fft.fft2(gray)
    fft_shift = np.fft.fftshift(fft)

    magnitude = np.abs(fft_shift)

    frequency_energy = np.mean(np.log1p(magnitude))

    # High-frequency region
    y_start = int(height * 0.25)
    y_end = int(height * 0.75)

    x_start = int(width * 0.25)
    x_end = int(width * 0.75)

    high_frequency_energy = np.mean(
        magnitude[y_start:y_end, x_start:x_end]
    )

    # ==========================================
    # STORE RESULTS
    # ==========================================

    result = {
        "image_width": width,
        "image_height": height,
        "brightness": round(float(brightness), 2),
        "contrast": round(float(contrast), 2),
        "edge_strength": round(float(edge_strength), 2),
        "frequency_energy": round(float(frequency_energy), 2),
        "high_frequency_energy": round(float(high_frequency_energy), 2)
    }

    return result


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    from pathlib import Path

    folders = {
        "REAL": Path("AI/samples/genuine"),
        "SYNTHETIC": Path("AI/samples/synthetic")
    }

    print("\n================================")
    print(" VERITRACE FORENSIC ANALYSIS")
    print("================================")

    for actual_label, folder in folders.items():

        for image_path in folder.iterdir():

            if image_path.suffix.lower() not in [
                ".jpg", ".jpeg", ".png", ".webp"
            ]:
                continue

            result = analyze_image(str(image_path))

            print("\n--------------------------------")
            print(f"Image  : {image_path.name}")
            print(f"Actual : {actual_label}")
            print("--------------------------------")

            for key, value in result.items():
                print(f"{key}: {value}")

    print("\n================================")
    print("       ANALYSIS COMPLETE")
    print("================================")