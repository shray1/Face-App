"""Image utility helpers: thumbnail generation and face cropping."""

from __future__ import annotations

from pathlib import Path

from PIL import Image as PilImage
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _pil_to_qpixmap(pil_img: PilImage.Image) -> QPixmap:
    """Convert a PIL Image (RGB or RGBA) to a QPixmap."""
    pil_img = pil_img.convert("RGBA")
    data = pil_img.tobytes("raw", "RGBA")
    qimage = QImage(data, pil_img.width, pil_img.height, QImage.Format.Format_RGBA8888)
    return QPixmap.fromImage(qimage)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def make_thumbnail(image_path: str | Path, size: tuple[int, int] = (200, 200)) -> QPixmap:
    """Load *image_path* and return a QPixmap thumbnail that fits within *size*.

    Aspect ratio is preserved; the image is never upscaled.

    Args:
        image_path: Path to the source image file.
        size:       Maximum (width, height) in pixels.

    Returns:
        A :class:`QPixmap` ready for display, or a blank pixmap on error.
    """
    try:
        with PilImage.open(image_path) as img:
            img = img.convert("RGB")
            img.thumbnail(size, PilImage.LANCZOS)
            return _pil_to_qpixmap(img)
    except Exception:
        # Return a transparent placeholder so callers never receive None.
        blank = QPixmap(*size)
        blank.fill(Qt.GlobalColor.transparent)
        return blank


def crop_face(
    image_path: str | Path,
    bbox: tuple[int, int, int, int],
    padding: int = 20,
) -> QPixmap:
    """Crop a face region from *image_path* and return it as a QPixmap.

    Args:
        image_path: Path to the source image file.
        bbox:       ``(x, y, w, h)`` bounding box in absolute pixels.
        padding:    Extra pixels to include around the detected face box.

    Returns:
        A :class:`QPixmap` of the cropped face region, or a blank pixmap on error.
    """
    try:
        x, y, w, h = bbox
        with PilImage.open(image_path) as img:
            img = img.convert("RGB")
            img_w, img_h = img.size
            left   = max(0, x - padding)
            top    = max(0, y - padding)
            right  = min(img_w, x + w + padding)
            bottom = min(img_h, y + h + padding)
            cropped = img.crop((left, top, right, bottom))
            return _pil_to_qpixmap(cropped)
    except Exception:
        blank = QPixmap(100, 100)
        blank.fill(Qt.GlobalColor.transparent)
        return blank
