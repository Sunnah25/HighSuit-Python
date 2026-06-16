from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette


# ------------------------------------------------------------------ #
#  Colour palette — used everywhere in the UI                         #
# ------------------------------------------------------------------ #
class Colours:
    BACKGROUND   = "#1a1a2e"   # Deep navy
    SURFACE      = "#16213e"   # Slightly lighter navy
    CARD_GREEN   = "#0f3460"   # Dark blue-green for table
    ACCENT       = "#e94560"   # Red accent
    GOLD         = "#f5a623"   # Gold for scores / highlights
    TEXT_PRIMARY = "#eaeaea"   # Off-white
    TEXT_MUTED   = "#a0a0b0"   # Grey
    BUTTON_BG    = "#e94560"   # Button background
    BUTTON_HOVER = "#c73652"   # Button hover


# ------------------------------------------------------------------ #
#  Reusable styled button                                             #
# ------------------------------------------------------------------ #
class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(45)
        self.setFont(QFont("Arial", 11, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colours.BUTTON_BG};
                color: {Colours.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 0 24px;
            }}
            QPushButton:hover {{
                background-color: {Colours.BUTTON_HOVER};
            }}
            QPushButton:pressed {{
                background-color: #a02d45;
            }}
            QPushButton:disabled {{
                background-color: #555566;
                color: #888899;
            }}
        """)


# ------------------------------------------------------------------ #
#  Welcome / Start screen                                             #
# ------------------------------------------------------------------ #
class WelcomeScreen(QWidget):
    def __init__(self, on_start):
        super().__init__()
        self.on_start = on_start
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {Colours.BACKGROUND};")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(24)
        self.setLayout(layout)

        # Title
        title = QLabel("🃏 HighSuit")
        title.setFont(QFont("Arial", 48, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {Colours.GOLD};")
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel("The Card Game")
        subtitle.setFont(QFont("Arial", 18))
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet(f"color: {Colours.TEXT_MUTED};")
        layout.addWidget(subtitle)

        layout.addSpacing(20)

        # Start button
        start_btn = StyledButton("▶  Start Game")
        start_btn.setFixedWidth(220)
        start_btn.clicked.connect(self.on_start)
        layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        # Version label
        version = QLabel("v1.0.0")
        version.setFont(QFont("Arial", 9))
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet(f"color: {Colours.TEXT_MUTED};")
        layout.addWidget(version)


# ------------------------------------------------------------------ #
#  Placeholder game screen (Days 8–10 will fill this in)             #
# ------------------------------------------------------------------ #
class GameScreen(QWidget):
    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {Colours.CARD_GREEN};")

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)
        self.setLayout(layout)

        label = QLabel("Game Screen — Coming Soon")
        label.setFont(QFont("Arial", 22, QFont.Bold))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet(f"color: {Colours.TEXT_PRIMARY};")
        layout.addWidget(label)

        back_btn = StyledButton("← Back to Menu")
        back_btn.setFixedWidth(200)
        back_btn.clicked.connect(self.on_back)
        layout.addWidget(back_btn, alignment=Qt.AlignCenter)


# ------------------------------------------------------------------ #
#  Main Window                                                        #
# ------------------------------------------------------------------ #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HighSuit Card Game")
        self.setMinimumSize(900, 650)
        self.resize(1024, 720)
        self._centre_on_screen()
        self._build_ui()

    def _centre_on_screen(self):
        """Open the window in the centre of the screen."""
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size   = self.geometry()
        self.move(
            (screen.width()  - size.width())  // 2,
            (screen.height() - size.height()) // 2,
        )

    def _build_ui(self):
        # Stack holds multiple screens; we swap between them
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Screens
        self.welcome_screen = WelcomeScreen(on_start=self._show_game)
        self.game_screen    = GameScreen(on_back=self._show_welcome)

        self.stack.addWidget(self.welcome_screen)  # index 0
        self.stack.addWidget(self.game_screen)     # index 1

        self.stack.setCurrentIndex(0)

    def _show_game(self):
        self.stack.setCurrentIndex(1)

    def _show_welcome(self):
        self.stack.setCurrentIndex(0)