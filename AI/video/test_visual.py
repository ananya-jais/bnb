import sys
sys.path.insert(0, r"C:\Users\Kanchan\OneDrive\Desktop\bnb")

from visual_detector import analyze_video_visual


REAL_VIDEO = r"C:\Users\Kanchan\OneDrive\Desktop\bnb\AI\samples\video\real1.mp4"
FAKE_VIDEO = r"C:\Users\Kanchan\OneDrive\Desktop\bnb\AI\samples\video\fake.mp4"


print("\n========================================")
print("        VERITRACE VISUAL TEST")
print("========================================")


print("\n========== REAL VIDEO ==========")

real_result = analyze_video_visual(
    REAL_VIDEO,
    sample_count=12
)

for key, value in real_result.items():

    if key != "frame_results":
        print(f"{key}: {value}")


print("\n========== FAKE VIDEO ==========")

fake_result = analyze_video_visual(
    FAKE_VIDEO,
    sample_count=12
)

for key, value in fake_result.items():

    if key != "frame_results":
        print(f"{key}: {value}")


print("\n========================================")