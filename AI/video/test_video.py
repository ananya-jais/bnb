import cv2
import os

from AI.video.video_detector import extract_frames


def save_debug_frames(video_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    frames = extract_frames(video_path, max_frames=12)

    for i, frame in enumerate(frames):
        output_path = os.path.join(
            output_folder,
            f"frame_{i + 1:02d}.jpg"
        )

        cv2.imwrite(output_path, frame)

    print(f"Saved {len(frames)} frames to:")
    print(output_folder)


# Debug the real video
save_debug_frames(
    "AI/samples/video/real1.mp4",
    "AI/samples/video/debug/real"
)

# Debug the AI-manipulated video
save_debug_frames(
    "AI/samples/video/fake1.mp4",
    "AI/samples/video/debug/fake"
)