from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QLineEdit,
    QSpinBox, QFrame, QGraphicsDropShadowEffect
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient

from src.game import Game, GameState
from src.card import Suit


# ------------------------------------------------------------------ #
#  Design Tokens                                                      #
# ------------------------------------------------------------------ #
class C:
    # Felt table green
    FELT          = "#1B4332"
    FELT_DARK     = "#0D2B20"
    FELT_LIGHT    = "#2D6A4F"

    # Card & surface colours
    CARD_WHITE    = "#F7F3E9"   # Warm cream — card face
    CARD_BORDER   = "#C8B89A"   # Tan card border

    # Accents
    GOLD          = "#D4A843"   # Warm gold — scores, highlights
    GOLD_DARK     = "#A07830"
    RED           = "#C0392B"   # Hearts/Diamonds red
    DARK_RED      = "#922B21"

    # Text
    TEXT_LIGHT    = "#F7F3E9"   # On dark backgrounds
    TEXT_DARK     = "#1A1A1A"   # On card faces
    TEXT_MUTED    = "#A8C5B5"   # Subdued on felt

    # UI surfaces
    PANEL         = "#163D2B"   # Slightly lighter than felt
    INPUT_BG      = "#0F2D1E"
    INPUT_BORDER  = "#2D6A4F"
    INPUT_FOCUS   = "#D4A843"


# ------------------------------------------------------------------ #
#  Reusable Widgets                                                   #
# ------------------------------------------------------------------ #
class GoldButton(QPushButton):
    """Primary action button — gold on felt."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(48)
        self.setFont(QFont("Georgia", 12, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {C.GOLD};
                color: {C.TEXT_DARK};
                border: none;
                border-radius: 6px;
                padding: 0 32px;
                letter-spacing: 1px;
            }}
            QPushButton:hover {{
                background-color: {C.GOLD_DARK};
                color: {C.TEXT_LIGHT};
            }}
            QPushButton:pressed {{
                background-color: #8A6520;
            }}
            QPushButton:disabled {{
                background-color: #3D5A4A;
                color: #6A8A7A;
            }}
        """)


class GhostButton(QPushButton):
    """Secondary button — outlined, no fill."""
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(40)
        self.setFont(QFont("Georgia", 10))
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                color: {C.TEXT_MUTED};
                border: 1px solid {C.FELT_LIGHT};
                border-radius: 6px;
                padding: 0 20px;
            }}
            QPushButton:hover {{
                border-color: {C.GOLD};
                color: {C.GOLD};
            }}
        """)


class StyledInput(QLineEdit):
    """Styled text input for player names."""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setFixedHeight(42)
        self.setFont(QFont("Arial", 12))
        self.setStyleSheet(f"""
            QLineEdit {{
                background-color: {C.INPUT_BG};
                color: {C.TEXT_LIGHT};
                border: 1px solid {C.INPUT_BORDER};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QLineEdit:focus {{
                border: 1px solid {C.INPUT_FOCUS};
            }}
            QLineEdit::placeholder {{
                color: #4A7A60;
            }}
        """)


class Divider(QFrame):
    """Horizontal rule."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background-color: {C.FELT_LIGHT}; border: none;")


class SuitBadge(QLabel):
    """Displays a suit symbol with colour."""
    SYMBOLS = {
        "Spades":   ("♠", C.TEXT_LIGHT),
        "Hearts":   ("♥", C.RED),
        "Diamonds": ("♦", C.RED),
        "Clubs":    ("♣", C.TEXT_LIGHT),
    }

    def __init__(self, suit_name, size=28, parent=None):
        super().__init__(parent)
        symbol, colour = self.SYMBOLS.get(suit_name, ("?", C.GOLD))
        self.setText(symbol)
        self.setFont(QFont("Arial", size))
        self.setStyleSheet(f"color: {colour}; background: transparent;")
        self.setAlignment(Qt.AlignCenter)


# ------------------------------------------------------------------ #
#  Welcome Screen                                                     #
# ------------------------------------------------------------------ #
class WelcomeScreen(QWidget):
    def __init__(self, on_start):
        super().__init__()
        self.on_start = on_start
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(0)
        self.setLayout(root)

        # ── Suit row ──────────────────────────────────────────────
        suits_row = QHBoxLayout()
        suits_row.setSpacing(24)
        suits_row.setAlignment(Qt.AlignCenter)
        for suit in ["Spades", "Hearts", "Diamonds", "Clubs"]:
            suits_row.addWidget(SuitBadge(suit, size=36))
        root.addLayout(suits_row)

        root.addSpacing(16)
        root.addWidget(Divider())
        root.addSpacing(32)

        # ── Title ─────────────────────────────────────────────────
        title = QLabel("HIGHSUIT")
        title.setFont(QFont("Georgia", 52, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {C.GOLD}; background: transparent; letter-spacing: 8px;")
        root.addWidget(title)

        tagline = QLabel("A game of cards, strategy & suits")
        tagline.setFont(QFont("Georgia", 13))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        root.addWidget(tagline)

        root.addSpacing(48)

        # ── Buttons ───────────────────────────────────────────────
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(12)
        btn_layout.setAlignment(Qt.AlignCenter)

        start_btn = GoldButton("  DEAL ME IN  ")
        start_btn.setFixedWidth(220)
        start_btn.clicked.connect(self.on_start)
        btn_layout.addWidget(start_btn, alignment=Qt.AlignCenter)

        root.addLayout(btn_layout)
        root.addSpacing(48)

        root.addWidget(Divider())
        root.addSpacing(16)

        # ── Footer suits ──────────────────────────────────────────
        footer = QLabel("♠  ♥  ♦  ♣")
        footer.setFont(QFont("Arial", 14))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {C.FELT_LIGHT}; background: transparent;")
        root.addWidget(footer)


# ------------------------------------------------------------------ #
#  Player Setup Screen                                                #
# ------------------------------------------------------------------ #
class SetupScreen(QWidget):
    """
    Lets the player enter their name and choose number of rounds
    before the game starts.
    """
    def __init__(self, on_start_game, on_back):
        super().__init__()
        self.on_start_game = on_start_game
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT};")

        root = QVBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(0)
        self.setLayout(root)

        # ── Panel card ────────────────────────────────────────────
        panel = QWidget()
        panel.setFixedWidth(420)
        panel.setStyleSheet(f"""
            background-color: {C.PANEL};
            border-radius: 12px;
            border: 1px solid {C.FELT_LIGHT};
        """)

        panel_layout = QVBoxLayout()
        panel_layout.setContentsMargins(36, 36, 36, 36)
        panel_layout.setSpacing(20)
        panel.setLayout(panel_layout)

        # Title
        title = QLabel("New Game")
        title.setFont(QFont("Georgia", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {C.GOLD}; background: transparent; border: none;")
        panel_layout.addWidget(title)

        panel_layout.addWidget(Divider())

        # Player name
        name_label = QLabel("Your Name")
        name_label.setFont(QFont("Arial", 10))
        name_label.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent; border: none;")
        panel_layout.addWidget(name_label)

        self.name_input = StyledInput(placeholder="Enter your name...")
        self.name_input.setMaxLength(20)
        panel_layout.addWidget(self.name_input)

        # Number of rounds
        rounds_label = QLabel("Number of Rounds")
        rounds_label.setFont(QFont("Arial", 10))
        rounds_label.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent; border: none;")
        panel_layout.addWidget(rounds_label)

        self.rounds_spin = QSpinBox()
        self.rounds_spin.setRange(1, 10)
        self.rounds_spin.setValue(3)
        self.rounds_spin.setFixedHeight(42)
        self.rounds_spin.setFont(QFont("Arial", 12))
        self.rounds_spin.setStyleSheet(f"""
            QSpinBox {{
                background-color: {C.INPUT_BG};
                color: {C.TEXT_LIGHT};
                border: 1px solid {C.INPUT_BORDER};
                border-radius: 6px;
                padding: 0 14px;
            }}
            QSpinBox:focus {{
                border: 1px solid {C.INPUT_FOCUS};
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                width: 28px;
                background-color: {C.FELT_LIGHT};
                border: none;
                border-radius: 3px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: {C.GOLD};
            }}
        """)
        panel_layout.addWidget(self.rounds_spin)

        panel_layout.addSpacing(8)
        panel_layout.addWidget(Divider())
        panel_layout.addSpacing(8)

        # Error label (hidden until needed)
        self.error_label = QLabel("")
        self.error_label.setFont(QFont("Arial", 10))
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(f"color: {C.RED}; background: transparent; border: none;")
        self.error_label.hide()
        panel_layout.addWidget(self.error_label)

        # Start button
        self.start_btn = GoldButton("Start Game  →")
        self.start_btn.clicked.connect(self._on_start_clicked)
        panel_layout.addWidget(self.start_btn)

        # Back button
        back_btn = GhostButton("← Back to Menu")
        back_btn.clicked.connect(self.on_back)
        panel_layout.addWidget(back_btn)

        root.addWidget(panel, alignment=Qt.AlignCenter)

    def _on_start_clicked(self):
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Please enter your name to continue.")
            self.error_label.show()
            return
        self.error_label.hide()
        rounds = self.rounds_spin.value()
        self.on_start_game(name, rounds)

    def reset(self):
        """Clear inputs when returning to this screen."""
        self.name_input.clear()
        self.rounds_spin.setValue(3)
        self.error_label.hide()


# ------------------------------------------------------------------ #
#  Placeholder Game Screen (Days 9–10 will replace this)             #
# ------------------------------------------------------------------ #
class GameScreen(QWidget):
    def __init__(self, on_menu):
        super().__init__()
        self.on_menu = on_menu
        self.game = None
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT_DARK};")
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)

        self.info_label = QLabel("Game loading...")
        self.info_label.setFont(QFont("Georgia", 18))
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_label.setStyleSheet(f"color: {C.TEXT_LIGHT}; background: transparent;")
        layout.addWidget(self.info_label)

        menu_btn = GhostButton("← Back to Menu")
        menu_btn.clicked.connect(self.on_menu)
        layout.addWidget(menu_btn, alignment=Qt.AlignCenter)

    def load_game(self, player_name, total_rounds):
        """Called from MainWindow when a new game is starting."""
        self.game = Game([player_name], total_rounds=total_rounds)
        self.info_label.setText(
            f"Welcome, {player_name}!\n"
            f"{total_rounds}-round game ready.\n\n"
            f"Full game UI coming Day 9 & 10!"
        )


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
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width()  - size.width())  // 2,
            (screen.height() - size.height()) // 2,
        )

    def _build_ui(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen = WelcomeScreen(on_start=self._show_setup)
        self.setup_screen   = SetupScreen(
            on_start_game=self._start_game,
            on_back=self._show_welcome
        )
        self.game_screen    = GameScreen(on_menu=self._show_welcome)

        self.stack.addWidget(self.welcome_screen)  # index 0
        self.stack.addWidget(self.setup_screen)    # index 1
        self.stack.addWidget(self.game_screen)     # index 2

        self.stack.setCurrentIndex(0)

    def _show_welcome(self):
        self.setup_screen.reset()
        self.stack.setCurrentIndex(0)

    def _show_setup(self):
        self.stack.setCurrentIndex(1)

    def _start_game(self, player_name, total_rounds):
        self.game_screen.load_game(player_name, total_rounds)
        self.stack.setCurrentIndex(2)