"""Application entry point."""

from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication

from face_app.db.session import init_db
from face_app.ui.main_window import MainWindow


def main() -> None:
    # Initialise the SQLite database (creates tables on first run).
    init_db()

    app = QApplication(sys.argv)
    app.setApplicationName("Face App")
    app.setOrganizationName("FaceApp")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
