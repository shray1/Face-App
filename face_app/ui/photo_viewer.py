"""Photo viewer: shows all photos in which a selected person appears."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget


class PhotoViewer(QScrollArea):
    """Scrollable list of photo thumbnails for a single person."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)

        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self.setWidget(self._container)

    def show_person(self, person_id: int, faces: list) -> None:
        """Populate the viewer with thumbnails for *person_id*.

        Args:
            person_id: The Person DB id being viewed.
            faces:     List of Face ORM objects belonging to this person.
        """
        # Clear existing widgets.
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not faces:
            label = QLabel("No photos found for this person.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._layout.addWidget(label)
            return

        # Placeholder — thumbnails wired up in a later session.
        for face in faces:
            label = QLabel(f"Face {face.id} — {face.image.file_path}")
            self._layout.addWidget(label)
