"""Local face enrolment and recognition with OpenCV YuNet + SFace."""

import os
import threading
from functools import lru_cache
from pathlib import Path

import cv2
import numpy as np
from django.conf import settings

from store_app.models import faceID


DETECTOR_MODEL = Path(settings.BASE_DIR) / "static/model/face_detection_yunet_2023mar.onnx"
RECOGNIZER_MODEL = Path(settings.BASE_DIR) / "static/model/face_recognition_sface_2021dec.onnx"
MATCH_THRESHOLD = float(os.environ.get("FACE_MATCH_THRESHOLD", "0.363"))
MODEL_LOCK = threading.Lock()


class FaceRecognitionError(RuntimeError):
    """Base exception for local face recognition failures."""


class FaceNotFoundError(FaceRecognitionError):
    """Raised when no usable face is found in an image."""


@lru_cache(maxsize=1)
def _models():
    missing = [path.name for path in (DETECTOR_MODEL, RECOGNIZER_MODEL) if not path.exists()]
    if missing:
        raise FaceRecognitionError(f"缺少 OpenCV 模型：{', '.join(missing)}")

    detector = cv2.FaceDetectorYN.create(str(DETECTOR_MODEL), "", (320, 320), 0.9, 0.3, 5000)
    recognizer = cv2.FaceRecognizerSF.create(str(RECOGNIZER_MODEL), "")
    return detector, recognizer


def _read_image(path):
    path = Path(path)
    image = cv2.imdecode(np.frombuffer(path.read_bytes(), dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise FaceRecognitionError(f"無法讀取圖片：{path.name}")
    return image


def extract_embedding(path):
    """Extract one normalized SFace embedding from an image path."""
    image = _read_image(path)
    height, width = image.shape[:2]
    detector, recognizer = _models()

    with MODEL_LOCK:
        detector.setInputSize((width, height))
        _, faces = detector.detect(image)
        if faces is None or len(faces) == 0:
            raise FaceNotFoundError("照片中沒有偵測到清楚的人臉。")

        # Prefer the largest detected face so background bystanders are ignored.
        face = max(faces, key=lambda detected: float(detected[2] * detected[3]))
        aligned = recognizer.alignCrop(image, face)
        embedding = recognizer.feature(aligned).flatten().astype(np.float32)

    norm = float(np.linalg.norm(embedding))
    if norm == 0:
        raise FaceRecognitionError("無法建立有效的人臉特徵。")
    return (embedding / norm).tolist()


def enroll_member(account):
    """Store embeddings from a member's three registration photos locally."""
    embeddings = [
        extract_embedding(account.cPhoto1.path),
        extract_embedding(account.cPhoto2.path),
        extract_embedding(account.cPhoto3.path),
    ]
    profile, _ = faceID.objects.get_or_create(faceID_name=account.cName)
    profile.faceID_embeddings = embeddings
    profile.save(update_fields=["faceID_embeddings"])
    return profile


def recognize_member(path, threshold=MATCH_THRESHOLD):
    """Return ``(member_name, cosine_score)`` for the closest local profile."""
    candidate = np.asarray(extract_embedding(path), dtype=np.float32)
    best_name = ""
    best_score = -1.0

    for profile in faceID.objects.exclude(faceID_embeddings=[]):
        for stored in profile.faceID_embeddings:
            enrolled = np.asarray(stored, dtype=np.float32)
            if enrolled.shape != candidate.shape:
                continue
            score = float(np.dot(candidate, enrolled))
            if score > best_score:
                best_name, best_score = profile.faceID_name, score

    if best_score < threshold:
        return "", best_score
    return best_name, best_score
