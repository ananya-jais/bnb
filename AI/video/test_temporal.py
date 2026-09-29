import cv2
import mediapipe as mp
import numpy as np


# -----------------------------
# SETTINGS
# -----------------------------

video_path = "AI/samples/video/fake1.mp4"

# Check every 5th frame
FRAME_STEP = 5


# -----------------------------
# MEDIAPIPE FACE DETECTOR
# -----------------------------

BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode


options = FaceDetectorOptions(
    base_options=BaseOptions(
        model_asset_path="face_detector.tflite"
    ),
    running_mode=VisionRunningMode.IMAGE,
    min_detection_confidence=0.5
)


# -----------------------------
# OPEN VIDEO
# -----------------------------

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Could not open video")
    exit()


previous_face = None
differences = []

frame_number = 0
analyzed_frames = 0


# -----------------------------
# ANALYZE FRAMES
# -----------------------------

with FaceDetector.create_from_options(options) as detector:

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame_number += 1

        # Only analyze every 5th frame
        if frame_number % FRAME_STEP != 0:
            continue

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = detector.detect(mp_image)

        if not result.detections:
            continue

        detection = result.detections[0]

        bounding_box = detection.bounding_box

        x = bounding_box.origin_x
        y = bounding_box.origin_y
        w = bounding_box.width
        h = bounding_box.height

        # Make sure coordinates stay inside the image
        height, width = frame.shape[:2]

        x1 = max(0, x)
        y1 = max(0, y)
        x2 = min(width, x + w)
        y2 = min(height, y + h)

        face = frame[y1:y2, x1:x2]

        if face.size == 0:
            continue

        # Resize every face to the same size
        face = cv2.resize(face, (128, 128))

        # Convert to grayscale
        face_gray = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)

        # Normalize pixel values
        face_gray = face_gray.astype(np.float32) / 255.0

        # Compare with previous frame
        if previous_face is not None:

            difference = np.mean(
                np.abs(face_gray - previous_face)
            )

            differences.append(difference)

        previous_face = face_gray

        analyzed_frames += 1


cap.release()


# -----------------------------
# RESULTS
# -----------------------------

print("\n===== TEMPORAL ANALYSIS =====")

print("Video:", video_path)

print("Frames analyzed:", analyzed_frames)

print("Comparisons:", len(differences))


if differences:

    average_difference = np.mean(differences)

    std_difference = np.std(differences)

    maximum_difference = np.max(differences)

    print(
        "Average frame difference:",
        round(float(average_difference), 4)
    )

    print(
        "Difference standard deviation:",
        round(float(std_difference), 4)
    )

    print(
        "Maximum frame difference:",
        round(float(maximum_difference), 4)
    )

else:

    print("Not enough frames for temporal analysis.")