import cv2
import mediapipe as mp


# Create MediaPipe Face Detector
BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

video_path = "AI/samples/video/fake1.mp4"

cap = cv2.VideoCapture(video_path)

if not cap.isOpened():
    print("Could not open video")
    exit()

frame_count = 0
faces_found = 0


options = FaceDetectorOptions(
    base_options=BaseOptions(
        model_asset_path="face_detector.tflite"
    ),
    running_mode=VisionRunningMode.IMAGE,
    min_detection_confidence=0.5
)


with FaceDetector.create_from_options(options) as detector:

    while True:
        success, frame = cap.read()

        if not success:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        result = detector.detect(mp_image)

        frame_count += 1

        if result.detections:
            faces_found += 1


cap.release()


print("===== FACE DETECTION TEST =====")
print("Total frames checked:", frame_count)
print("Frames with face detected:", faces_found)