"""Human-in-the-loop review dialog: show two face crops and ask for a decision."""

from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from face_app.db.models import DecisionEnum


class ReviewDialog(QDialog):
    """Modal dialog presenting two face crops for the user to compare.

    After the dialog closes, read :attr:`decision` for the user's choice.
    """

    def __init__(
        self,
        pixmap_a: QPixmap,
        pixmap_b: QPixmap,
        face_a_id: int,
        face_b_id: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Are these the same person?")
        self.setModal(True)

        self.face_a_id = face_a_id
        self.face_b_id = face_b_id
        self.decision: DecisionEnum = DecisionEnum.skip

        self._build_ui(pixmap_a, pixmap_b)

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_ui(self, pixmap_a: QPixmap, pixmap_b: QPixmap) -> None:
        root = QVBoxLayout(self)

        instruction = QLabel("Are these two face crops the same person?")
        instruction.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instruction.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 8px;")
        root.addWidget(instruction)

        # Face crops side by side.
        crops_row = QHBoxLayout()
        for pixmap in (pixmap_a, pixmap_b):
            label = QLabel()
            label.setPixmap(
                pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            )
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            crops_row.addWidget(label)
        root.addLayout(crops_row)

        # Decision buttons.
        btn_row = QHBoxLayout()

        same_btn = QPushButton("Same Person ✓")
        same_btn.setStyleSheet("background-color: #4caf50; color: white; padding: 8px 20px;")
        same_btn.clicked.connect(self._on_same)

        diff_btn = QPushButton("Different Person ✗")
        diff_btn.setStyleSheet("background-color: #f44336; color: white; padding: 8px 20px;")
        diff_btn.clicked.connect(self._on_different)

        skip_btn = QPushButton("Skip")
        skip_btn.setStyleSheet("padding: 8px 20px;")
        skip_btn.clicked.connect(self._on_skip)

        btn_row.addWidget(same_btn)
        btn_row.addWidget(diff_btn)
        btn_row.addWidget(skip_btn)
        root.addLayout(btn_row)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_same(self) -> None:
        self.decision = DecisionEnum.same
        self.accept()

    def _on_different(self) -> None:
        self.decision = DecisionEnum.different
        self.accept()

    def _on_skip(self) -> None:
        self.decision = DecisionEnum.skip
        self.reject()
