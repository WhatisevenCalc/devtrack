# DevTrack - Development Activity Tracker
# Copyright (c) 2026 Ivan Timov. All rights reserved.
# Proprietary and confidential.

import sys
from PyQt6.QtWidgets import QApplication
from src.gui import DevTrackWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("DevTrack")
    app.setQuitOnLastWindowClosed(False)

    window = DevTrackWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
