"""Face detection and 128-d embedding extraction.

Primary backend: ``face_recognition`` (dlib HOG/CNN).
Fallback:        ``deepface`` (used when face_recognition is unavailable).
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

import numpy as np


@dataclass
class DetectedFace:
    """A single face detected within an image."""

    bbox_x: int
    bbox_y: int
    bbox_w: int
    bbox_h: int
    embedding: bytes          # 128 × float32 packed as little-endian bytes (512 B)
    confidence: float = 1.0   # detector-specific confidence score


def embedding_to_bytes(vec: np.ndarray) -> bytes:
    """Pack a (128,) float32 array into raw bytes."""
    arr = np.asarray(vec, dtype=np.float32).flatten()
    if arr.shape != (128,):
        raise ValueError(f"Expected 128-element embedding, got shape {arr.shape}")
    return arr.tobytes()


def bytes_to_embedding(raw: bytes) -> np.ndarray:
    """Unpack raw bytes back into a (128,) float32 numpy array."""
    return np.frombuffer(raw, dtype=np.float32).copy()


# ---------------------------------------------------------------------------
# face_recognition backend
# ---------------------------------------------------------------------------

def _detect_with_face_recognition(image_path: Path) -> list[DetectedFace]:
    import face_recognition  # type: ignore[import]

    image = face_recognition.load_image_file(str(image_path))
    # Use HOG model (fast); swap to "cnn" for higher accuracy on GPU.
    locations = face_recognition.face_locations(image, model="hog")
    if not locations:
        return []
    encodings = face_recognition.face_encodings(image, locations)

    faces: list[DetectedFace] = []
    for (top, right, bottom, left), encoding in zip(locations, encodings):
        faces.append(
            DetectedFace(
                bbox_x=left,
                bbox_y=top,
                bbox_w=right - left,
                bbox_h=bottom - top,
                embedding=embedding_to_bytes(encoding),
                confidence=1.0,
            )
        )
    return faces


# ---------------------------------------------------------------------------
# deepface fallback backend
# ---------------------------------------------------------------------------

def _detect_with_deepface(image_path: Path) -> list[DetectedFace]:
    from deepface import DeepFace  # type: ignore[import]
    import cv2

    results = DeepFace.represent(
        img_path=str(image_path),
        model_name="Facenet",  # 128-d embeddings
        enforce_detection=False,
        detector_backend="opencv",
    )

    faces: list[DetectedFace] = []
    for r in results:
        region = r.get("facial_area", {})
        embedding_raw = r.get("embedding", [])
        if len(embedding_raw) != 128 or not region:
            continue
        faces.append(
            DetectedFace(
                bbox_x=region.get("x", 0),
                bbox_y=region.get("y", 0),
                bbox_w=region.get("w", 0),
                bbox_h=region.get("h", 0),
                embedding=embedding_to_bytes(np.array(embedding_raw, dtype=np.float32)),
                confidence=r.get("face_confidence", 1.0),
            )
        )
    return faces


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def detect_faces(image_path: str | Path) -> list[DetectedFace]:
    """Detect all faces in *image_path* and return their bounding boxes + embeddings.

    Tries ``face_recognition`` first; falls back to ``deepface`` if the
    primary library is not installed.

    Args:
        image_path: Absolute path to the image file.

    Returns:
        List of :class:`DetectedFace` instances (may be empty if no faces found).
    """
    path = Path(image_path).resolve()
    try:
        return _detect_with_face_recognition(path)
    except ImportError:
        pass

    try:
        return _detect_with_deepface(path)
    except ImportError:
        raise RuntimeError(
            "Neither 'face_recognition' nor 'deepface' is available. "
            "Install at least one of them to enable face detection."
        )
