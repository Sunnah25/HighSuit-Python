import sys
from PyQt5.QtWidgets import QApplication
from src.ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HighSuit Card Game")
    app.setStyle("Fusion")  # Clean cross-platform style

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()