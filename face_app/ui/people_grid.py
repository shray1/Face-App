"""Grid view displaying one card per identified person."""

from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QScrollArea, QGridLayout, QWidget


class PeopleGrid(QScrollArea):
    """Scrollable grid of person cards.

    Emits :attr:`person_selected` with the Person DB id when a card is clicked.
    """

    person_selected = pyqtSignal(int)  # person_id

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWidgetResizable(True)

        self._container = QWidget()
        self._grid = QGridLayout(self._container)
        self._grid.setContentsMargins(12, 12, 12, 12)
        self._grid.setSpacing(12)
        self.setWidget(self._container)

    def clear(self) -> None:
        """Remove all person cards from the grid."""
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def populate(self, persons: list) -> None:
        """Rebuild the grid from a list of Person ORM objects."""
        self.clear()
        # Placeholder — full implementation in a later session.
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtCore import Qt

        if not persons:
            label = QLabel("No people identified yet.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._grid.addWidget(label, 0, 0)
            return

        cols = 5
        for idx, person in enumerate(persons):
            label = QLabel(person.label or f"Person {person.id}")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            row, col = divmod(idx, cols)
            self._grid.addWidget(label, row, col)
