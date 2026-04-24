"""Root application window."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)


class MainWindow(QMainWindow):
    """The top-level application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Face App")
        self.resize(1200, 800)
        self._build_menu()
        self._build_central_widget()
        self.setStatusBar(QStatusBar())
        self.statusBar().showMessage("Ready — open a folder to begin scanning.")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_central_widget(self) -> None:
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)

        placeholder = QLabel(
            "Open a folder via  File → Open Folder  to start scanning for faces."
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #888; font-size: 16px;")
        layout.addWidget(placeholder)

        self.setCentralWidget(central)

    def _build_menu(self) -> None:
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&File")

        open_action = QAction("&Open Folder…", self)
        open_action.setShortcut("Ctrl+O")
        open_action.setStatusTip("Choose a folder to scan for images")
        open_action.triggered.connect(self._on_open_folder)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setStatusTip("Exit the application")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_open_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Image Folder",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )
        if folder:
            self.statusBar().showMessage(f"Selected folder: {folder}")
            # TODO: kick off background scan worker in a later session
