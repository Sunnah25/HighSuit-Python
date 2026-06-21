import sys
import os

# When running as PyInstaller bundle, add src to path
if getattr(sys, 'frozen', False):
    # Running as .exe — src files are in the same directory
    src_path = os.path.dirname(sys.executable)
    bundle_dir = sys._MEIPASS
    sys.path.insert(0, bundle_dir)
else:
    # Running from source — normal import
    src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, src_path)

from PyQt5.QtWidgets import QApplication

# Import works in both modes
try:
    from src.ui import MainWindow
except ModuleNotFoundError:
    from ui import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HighSuit Card Game")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()