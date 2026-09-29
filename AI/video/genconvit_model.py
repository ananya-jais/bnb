import cv2
import numpy as np
import onnxruntime as ort
import mediapipe as mp


MODEL_PATH = "AI/video/genconvit_ed_inference.onnx"
FACE_MODEL = "face_detector.tflite"

MEAN = np.array(
    [0.485, 0.456, 0.406],
    dtype=np.float32
).reshape(1, 3, 1, 1)

STD = np.array(
    [0.229, 0.224, 0.225],
    dtype=np.float32
).reshape(1, 3, 1, 1)


def load_model():
    return ort.InferenceSession(MODEL_PATH)


def extract_faces(video_path, max_frames=15):
    BaseOptions = mp.tasks.BaseOptions
    FaceDetector = mp.tasks.vision.FaceDetector
    FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
    RunningMode = mp.tasks.vision.RunningMode

    options = FaceDetectorOptions(
        base_options=BaseOptions(
            model_asset_path=FACE_MODEL
        ),
        running_mode=RunningMode.IMAGE,
        min_detection_confidence=0.5
    )

    cap = cv2.VideoCapture(video_path)

    faces = []

    with FaceDetector.create_from_options(options) as detector:

        while len(faces) < max_frames:

            ret, frame = cap.read()

            if not ret:
                break

            rgb = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB
            )

            mp_image = mp.Image(
                image_format=mp.ImageFormat.SRGB,
                data=rgb
            )

            result = detector.detect(mp_image)

            if not result.detections:
                continue

            bbox = result.detections[0].bounding_box

            x = max(0, bbox.origin_x)
            y = max(0, bbox.origin_y)

            x2 = min(
                rgb.shape[1],
                x + bbox.width
            )

            y2 = min(
                rgb.shape[0],
                y + bbox.height
            )

            face = rgb[y:y2, x:x2]

            if face.size == 0:
                continue

            face = cv2.resize(
                face,
                (224, 224)
            )

            faces.append(face)

    cap.release()

    return faces


def predict_video(video_path, max_frames=15):

    session = load_model()

    faces = extract_faces(
        video_path,
        max_frames
    )

    if not faces:
        return {
            "classification": "uncertain",
            "confidence": 0.0,
            "faces_used": 0
        }

    batch = np.stack([
        np.transpose(
            face.astype(np.float32) / 255.0,
            (2, 0, 1)
        )
        for face in faces
    ])

    batch = (batch - MEAN) / STD

    logits = session.run(
        None,
        {"input": batch}
    )[0]

    print("RAW MODEL OUTPUT:")
    print(logits)
    print("OUTPUT SHAPE:", logits.shape)

    scores = 1.0 / (
        1.0 + np.exp(-logits)
    )

    mean_scores = scores.mean(axis=0)

    predicted_class = int(
        np.argmax(mean_scores)
    )

    label = (
        "FAKE"
        if predicted_class == 0
        else "REAL"
    )

    confidence = float(
        mean_scores[predicted_class]
    )

    return {
        "classification": label,
        "confidence": round(confidence, 4),
        "faces_used": len(faces),
        "real_score": round(float(mean_scores[1]), 4),
        "fake_score": round(float(mean_scores[0]), 4)
    }