import sys
import json

sys.path.insert(
    0,
    r"C:\Users\Kanchan\OneDrive\Desktop\bnb"
)

sys.path.insert(
    0,
    r"C:\Users\Kanchan\auvire"
)

sys.path.insert(
    0,
    r"C:\Users\Kanchan\auvire\fairseq"
)

sys.path.insert(
    0,
    r"C:\Users\Kanchan\auvire\src\avhubert"
)

sys.path.insert(
    0,
    r"C:\Users\Kanchan\auvire\AI\video\audio"
)


from visual_detector import analyze_video_visual
from audio_detector import analyze_audio
from video_fusion import fuse_video_results
from src.itw import run_auvire


REAL_VIDEO = r"C:\Users\Kanchan\OneDrive\Desktop\bnb\AI\samples\video\real1.mp4"
FAKE_VIDEO = r"C:\Users\Kanchan\OneDrive\Desktop\bnb\AI\samples\video\fake.mp4"


def analyze_video(video_path):

    print("\n----------------------------------------")
    print("VIDEO:", video_path)
    print("----------------------------------------")

    print("\n[1/3] Visual analysis...")
    visual = analyze_video_visual(
        video_path,
        sample_count=12
    )

    print("\n[2/3] Audio analysis...")
    audio = analyze_audio(
        video_path
    )

    print("\n[3/3] AuViRe analysis...")

    auvire = run_auvire(
        model_training_dataset="lavdf",
        video_path=video_path,
        return_landmarks=False,
        device="cpu",
        core_response=False,
    )

    print("\n[FUSION] Combining results...")

    final_result = fuse_video_results(
        visual,
        audio,
        auvire
    )

    return final_result


print("\n========================================")
print("        VERITRACE VIDEO TEST")
print("========================================")


print("\n\n========== REAL VIDEO ==========")

real_result = analyze_video(
    REAL_VIDEO
)

print(
    json.dumps(
        real_result,
        indent=2,
        default=str
    )
)


print("\n\n========== FAKE VIDEO ==========")

fake_result = analyze_video(
    FAKE_VIDEO
)

print(
    json.dumps(
        fake_result,
        indent=2,
        default=str
    )
)


print("\n========================================")
print("             COMPLETE")
print("========================================")