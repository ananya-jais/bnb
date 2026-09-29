from pathlib import Path

genuine_folder = Path("AI/samples/genuine")
synthetic_folder = Path("AI/samples/synthetic")

print("\n========== VERITRACE TEST DATA ==========\n")

print("GENUINE IMAGES:")
for image in genuine_folder.iterdir():
    if image.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
        print("✓", image.name)

print("\nSYNTHETIC IMAGES:")
for image in synthetic_folder.iterdir():
    if image.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
        print("✓", image.name)

print("\n==========================================")
print("Test dataset ready!")
print("==========================================")