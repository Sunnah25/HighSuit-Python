from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QLineEdit,
    QSpinBox, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from src.game import Game, GameState
from src.card import Suit
from src.scores import ScoreManager


# ------------------------------------------------------------------ #
#  Design Tokens                                                      #
# ------------------------------------------------------------------ #
class C:
    FELT          = "#1B4332"
    FELT_DARK     = "#0D2B20"
    FELT_LIGHT    = "#2D6A4F"
    CARD_WHITE    = "#F7F3E9"
    CARD_BORDER   = "#C8B89A"
    GOLD          = "#D4A843"
    GOLD_DARK     = "#A07830"
    RED           = "#C0392B"
    TEXT_LIGHT    = "#F7F3E9"
    TEXT_DARK     = "#1A1A1A"
    TEXT_MUTED    = "#A8C5B5"
    PANEL         = "#163D2B"
    INPUT_BG      = "#0F2D1E"
    INPUT_BORDER  = "#2D6A4F"
    INPUT_FOCUS   = "#D4A843"
    SELECTED_BG   = "#3D2B00"


# ------------------------------------------------------------------ #
#  Reusable Widgets                                                   #
# ------------------------------------------------------------------ #
class GoldButton(QPushButton):
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
            }}
            QPushButton:hover {{ background-color: {C.GOLD_DARK}; color: {C.TEXT_LIGHT}; }}
            QPushButton:pressed {{ background-color: #8A6520; }}
            QPushButton:disabled {{ background-color: #3D5A4A; color: #6A8A7A; }}
        """)


class GhostButton(QPushButton):
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
            QPushButton:hover {{ border-color: {C.GOLD}; color: {C.GOLD}; }}
        """)


class StyledInput(QLineEdit):
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
            QLineEdit:focus {{ border: 1px solid {C.INPUT_FOCUS}; }}
        """)


class Divider(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background-color: {C.FELT_LIGHT}; border: none;")


class SuitBadge(QLabel):
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
#  Card Widget                                                        #
# ------------------------------------------------------------------ #
class CardWidget(QWidget):
    SUIT_SYMBOLS = {
        "Spades":   ("♠", C.TEXT_DARK),
        "Hearts":   ("♥", C.RED),
        "Diamonds": ("♦", C.RED),
        "Clubs":    ("♣", C.TEXT_DARK),
    }

    def __init__(self, card, index, on_toggle, parent=None):
        super().__init__(parent)
        self.card      = card
        self.index     = index
        self.on_toggle = on_toggle
        self.selected  = False
        self.setFixedSize(110, 160)
        self.setCursor(Qt.PointingHandCursor)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(4)
        self.setLayout(layout)

        suit_name = self.card.get_suit()[0]
        rank_name = self.card.get_rank()[0]
        symbol, colour = self.SUIT_SYMBOLS.get(suit_name, ("?", C.TEXT_DARK))

        self.rank_top = QLabel(rank_name)
        self.rank_top.setFont(QFont("Georgia", 16, QFont.Bold))
        self.rank_top.setStyleSheet(f"color: {colour}; background: transparent;")
        self.rank_top.setAlignment(Qt.AlignLeft)
        layout.addWidget(self.rank_top)

        self.suit_centre = QLabel(symbol)
        self.suit_centre.setFont(QFont("Arial", 42))
        self.suit_centre.setStyleSheet(f"color: {colour}; background: transparent;")
        self.suit_centre.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.suit_centre)

        self.rank_bot = QLabel(rank_name)
        self.rank_bot.setFont(QFont("Georgia", 16, QFont.Bold))
        self.rank_bot.setStyleSheet(f"color: {colour}; background: transparent;")
        self.rank_bot.setAlignment(Qt.AlignRight)
        layout.addWidget(self.rank_bot)

        self._apply_style()

    def _apply_style(self):
        if self.selected:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {C.SELECTED_BG};
                    border: 3px solid {C.GOLD};
                    border-radius: 10px;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {C.CARD_WHITE};
                    border: 2px solid {C.CARD_BORDER};
                    border-radius: 10px;
                }}
            """)

    def set_selected(self, selected):
        self.selected = selected
        self._apply_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.on_toggle(self.index)


# ------------------------------------------------------------------ #
#  Welcome Screen                                                     #
# ------------------------------------------------------------------ #
class WelcomeScreen(QWidget):
    def __init__(self, on_start, on_scores):
        super().__init__()
        self.on_start  = on_start
        self.on_scores = on_scores
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT};")
        root = QVBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(0)
        self.setLayout(root)

        suits_row = QHBoxLayout()
        suits_row.setSpacing(24)
        suits_row.setAlignment(Qt.AlignCenter)
        for suit in ["Spades", "Hearts", "Diamonds", "Clubs"]:
            suits_row.addWidget(SuitBadge(suit, size=36))
        root.addLayout(suits_row)

        root.addSpacing(16)
        root.addWidget(Divider())
        root.addSpacing(32)

        title = QLabel("HIGHSUIT")
        title.setFont(QFont("Georgia", 52, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {C.GOLD}; background: transparent; letter-spacing: 8px;"
        )
        root.addWidget(title)

        tagline = QLabel("A game of cards, strategy & suits")
        tagline.setFont(QFont("Georgia", 13))
        tagline.setAlignment(Qt.AlignCenter)
        tagline.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        root.addWidget(tagline)

        root.addSpacing(48)

        start_btn = GoldButton("  DEAL ME IN  ")
        start_btn.setFixedWidth(220)
        start_btn.clicked.connect(self.on_start)
        root.addWidget(start_btn, alignment=Qt.AlignCenter)

        root.addSpacing(12)

        scores_btn = GhostButton("🏆  High Scores")
        scores_btn.setFixedWidth(220)
        scores_btn.clicked.connect(self.on_scores)
        root.addWidget(scores_btn, alignment=Qt.AlignCenter)

        root.addSpacing(48)
        root.addWidget(Divider())
        root.addSpacing(16)

        footer = QLabel("♠  ♥  ♦  ♣")
        footer.setFont(QFont("Arial", 14))
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(f"color: {C.FELT_LIGHT}; background: transparent;")
        root.addWidget(footer)


# ------------------------------------------------------------------ #
#  Setup Screen                                                       #
# ------------------------------------------------------------------ #
class SetupScreen(QWidget):
    def __init__(self, on_start_game, on_back):
        super().__init__()
        self.on_start_game = on_start_game
        self.on_back       = on_back
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT};")
        root = QVBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        self.setLayout(root)

        panel = QWidget()
        panel.setFixedWidth(420)
        panel.setStyleSheet(f"""
            background-color: {C.PANEL};
            border-radius: 12px;
            border: 1px solid {C.FELT_LIGHT};
        """)
        pl = QVBoxLayout()
        pl.setContentsMargins(36, 36, 36, 36)
        pl.setSpacing(16)
        panel.setLayout(pl)

        title = QLabel("New Game")
        title.setFont(QFont("Georgia", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {C.GOLD}; background: transparent; border: none;"
        )
        pl.addWidget(title)
        pl.addWidget(Divider())

        name_lbl = QLabel("Your Name")
        name_lbl.setFont(QFont("Arial", 10))
        name_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        pl.addWidget(name_lbl)

        self.name_input = StyledInput(placeholder="Enter your name...")
        self.name_input.setMaxLength(20)
        pl.addWidget(self.name_input)

        rounds_lbl = QLabel("Number of Rounds")
        rounds_lbl.setFont(QFont("Arial", 10))
        rounds_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        pl.addWidget(rounds_lbl)

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
            QSpinBox:focus {{ border: 1px solid {C.INPUT_FOCUS}; }}
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
        pl.addWidget(self.rounds_spin)

        pl.addSpacing(4)
        pl.addWidget(Divider())
        pl.addSpacing(4)

        self.error_label = QLabel("")
        self.error_label.setFont(QFont("Arial", 10))
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(
            f"color: {C.RED}; background: transparent; border: none;"
        )
        self.error_label.hide()
        pl.addWidget(self.error_label)

        start_btn = GoldButton("Start Game  →")
        start_btn.clicked.connect(self._on_start_clicked)
        pl.addWidget(start_btn)

        back_btn = GhostButton("← Back to Menu")
        back_btn.clicked.connect(self.on_back)
        pl.addWidget(back_btn)

        root.addWidget(panel, alignment=Qt.AlignCenter)

    def _on_start_clicked(self):
        name = self.name_input.text().strip()
        if not name:
            self.error_label.setText("Please enter your name to continue.")
            self.error_label.show()
            return
        self.error_label.hide()
        self.on_start_game(name, self.rounds_spin.value())

    def reset(self):
        self.name_input.clear()
        self.rounds_spin.setValue(3)
        self.error_label.hide()


# ------------------------------------------------------------------ #
#  Summary Screen                                                     #
# ------------------------------------------------------------------ #
class SummaryScreen(QWidget):
    """
    Shown at end of game.
    Displays round-by-round breakdown and final score,
    then saves to the high score table.
    """

    def __init__(self, on_play_again, on_menu, on_scores):
        super().__init__()
        self.on_play_again = on_play_again
        self.on_menu       = on_menu
        self.on_scores     = on_scores
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT};")
        root = QVBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(0)
        self.setLayout(root)

        # Panel
        self.panel = QWidget()
        self.panel.setFixedWidth(480)
        self.panel.setStyleSheet(f"""
            background-color: {C.PANEL};
            border-radius: 12px;
            border: 1px solid {C.FELT_LIGHT};
        """)
        self.panel_layout = QVBoxLayout()
        self.panel_layout.setContentsMargins(36, 36, 36, 36)
        self.panel_layout.setSpacing(14)
        self.panel.setLayout(self.panel_layout)

        root.addWidget(self.panel, alignment=Qt.AlignCenter)

    def load_summary(self, player, score_manager):
        """Populate the summary with results from the finished game."""
        # Clear previous content
        while self.panel_layout.count():
            item = self.panel_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        name         = player.get_name()
        total        = player.get_total_score()
        round_scores = player.get_round_scores()

        # ── Header ────────────────────────────────────────────────
        trophy = QLabel("🏆")
        trophy.setFont(QFont("Arial", 36))
        trophy.setAlignment(Qt.AlignCenter)
        trophy.setStyleSheet("background: transparent; border: none;")
        self.panel_layout.addWidget(trophy)

        title = QLabel("Game Over!")
        title.setFont(QFont("Georgia", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {C.GOLD}; background: transparent; border: none;"
        )
        self.panel_layout.addWidget(title)

        player_lbl = QLabel(name)
        player_lbl.setFont(QFont("Georgia", 13))
        player_lbl.setAlignment(Qt.AlignCenter)
        player_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        self.panel_layout.addWidget(player_lbl)

        self.panel_layout.addWidget(Divider())

        # ── Round breakdown ───────────────────────────────────────
        rounds_title = QLabel("Round Breakdown")
        rounds_title.setFont(QFont("Arial", 10))
        rounds_title.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        self.panel_layout.addWidget(rounds_title)

        for i, score in enumerate(round_scores, 1):
            row = QHBoxLayout()
            r_lbl = QLabel(f"Round {i}")
            r_lbl.setFont(QFont("Arial", 12))
            r_lbl.setStyleSheet(
                f"color: {C.TEXT_LIGHT}; background: transparent; border: none;"
            )
            s_lbl = QLabel(f"+{score}")
            s_lbl.setFont(QFont("Georgia", 12, QFont.Bold))
            s_lbl.setAlignment(Qt.AlignRight)
            s_lbl.setStyleSheet(
                f"color: {C.GOLD}; background: transparent; border: none;"
            )
            row.addWidget(r_lbl)
            row.addWidget(s_lbl)
            self.panel_layout.addLayout(row)

        self.panel_layout.addWidget(Divider())

        # ── Total ─────────────────────────────────────────────────
        total_row = QHBoxLayout()
        t_lbl = QLabel("Total Score")
        t_lbl.setFont(QFont("Georgia", 14, QFont.Bold))
        t_lbl.setStyleSheet(
            f"color: {C.TEXT_LIGHT}; background: transparent; border: none;"
        )
        t_val = QLabel(str(total))
        t_val.setFont(QFont("Georgia", 22, QFont.Bold))
        t_val.setAlignment(Qt.AlignRight)
        t_val.setStyleSheet(
            f"color: {C.GOLD}; background: transparent; border: none;"
        )
        total_row.addWidget(t_lbl)
        total_row.addWidget(t_val)
        self.panel_layout.addLayout(total_row)

        # ── High score badge ──────────────────────────────────────
        rank = score_manager.get_rank(total)
        if score_manager.is_high_score(total):
            hs_lbl = QLabel(f"🎉  New High Score — Rank #{rank}!")
            hs_lbl.setFont(QFont("Georgia", 11, QFont.Bold))
            hs_lbl.setAlignment(Qt.AlignCenter)
            hs_lbl.setStyleSheet(
                f"color: {C.GOLD}; background: transparent; border: none;"
            )
            self.panel_layout.addWidget(hs_lbl)

        self.panel_layout.addWidget(Divider())

        # ── Buttons ───────────────────────────────────────────────
        play_btn = GoldButton("Play Again")
        play_btn.clicked.connect(self.on_play_again)
        self.panel_layout.addWidget(play_btn)

        scores_btn = GhostButton("🏆  View High Scores")
        scores_btn.clicked.connect(self.on_scores)
        self.panel_layout.addWidget(scores_btn)

        menu_btn = GhostButton("← Main Menu")
        menu_btn.clicked.connect(self.on_menu)
        self.panel_layout.addWidget(menu_btn)


# ------------------------------------------------------------------ #
#  High Score Screen                                                  #
# ------------------------------------------------------------------ #
class HighScoreScreen(QWidget):
    """Displays the top 10 all-time scores."""

    MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}

    def __init__(self, on_back):
        super().__init__()
        self.on_back = on_back
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT};")
        root = QVBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        root.setSpacing(0)
        self.setLayout(root)

        # Panel
        panel = QWidget()
        panel.setFixedWidth(520)
        panel.setStyleSheet(f"""
            background-color: {C.PANEL};
            border-radius: 12px;
            border: 1px solid {C.FELT_LIGHT};
        """)
        self.panel_layout = QVBoxLayout()
        self.panel_layout.setContentsMargins(36, 36, 36, 36)
        self.panel_layout.setSpacing(12)
        panel.setLayout(self.panel_layout)

        root.addWidget(panel, alignment=Qt.AlignCenter)

    def load_scores(self, score_manager):
        """Populate the leaderboard."""
        while self.panel_layout.count():
            item = self.panel_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        title = QLabel("🏆  High Scores")
        title.setFont(QFont("Georgia", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {C.GOLD}; background: transparent; border: none;"
        )
        self.panel_layout.addWidget(title)
        self.panel_layout.addWidget(Divider())

        entries = score_manager.get_entries()

        if not entries:
            empty = QLabel("No scores yet — play a game first!")
            empty.setFont(QFont("Georgia", 12))
            empty.setAlignment(Qt.AlignCenter)
            empty.setStyleSheet(
                f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
            )
            self.panel_layout.addWidget(empty)
        else:
            # Header row
            hdr = QHBoxLayout()
            for text, align in [
                ("#",     Qt.AlignLeft),
                ("Name",  Qt.AlignLeft),
                ("Score", Qt.AlignRight),
                ("Date",  Qt.AlignRight),
            ]:
                lbl = QLabel(text)
                lbl.setFont(QFont("Arial", 9))
                lbl.setAlignment(align)
                lbl.setStyleSheet(
                    f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
                )
                hdr.addWidget(lbl)
            self.panel_layout.addLayout(hdr)
            self.panel_layout.addWidget(Divider())

            for i, entry in enumerate(entries, 1):
                row  = QHBoxLayout()
                rank = self.MEDALS.get(i, str(i))

                rank_lbl = QLabel(str(rank))
                rank_lbl.setFixedWidth(32)
                rank_lbl.setFont(QFont("Arial", 13))
                rank_lbl.setStyleSheet(
                    f"color: {C.GOLD}; background: transparent; border: none;"
                )

                name_lbl = QLabel(entry.name)
                name_lbl.setFont(QFont("Georgia", 12))
                name_lbl.setStyleSheet(
                    f"color: {C.TEXT_LIGHT}; background: transparent; border: none;"
                )

                score_lbl = QLabel(str(entry.total_score))
                score_lbl.setFont(QFont("Georgia", 13, QFont.Bold))
                score_lbl.setAlignment(Qt.AlignRight)
                score_lbl.setStyleSheet(
                    f"color: {C.GOLD}; background: transparent; border: none;"
                )

                date_lbl = QLabel(entry.date)
                date_lbl.setFont(QFont("Arial", 9))
                date_lbl.setAlignment(Qt.AlignRight)
                date_lbl.setStyleSheet(
                    f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
                )

                row.addWidget(rank_lbl)
                row.addWidget(name_lbl)
                row.addWidget(score_lbl)
                row.addWidget(date_lbl)
                self.panel_layout.addLayout(row)

        self.panel_layout.addWidget(Divider())

        back_btn = GhostButton("← Back")
        back_btn.clicked.connect(self.on_back)
        self.panel_layout.addWidget(back_btn)


# ------------------------------------------------------------------ #
#  Game Screen                                                        #
# ------------------------------------------------------------------ #
class GameScreen(QWidget):
    def __init__(self, on_summary):
        super().__init__()
        self.on_summary   = on_summary
        self.game         = None
        self.card_widgets = []
        self.selected     = set()
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT_DARK};")
        root = QVBoxLayout()
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(16)
        self.setLayout(root)

        # Top bar
        top_bar = QHBoxLayout()
        self.round_label = QLabel("Round 1 of 3")
        self.round_label.setFont(QFont("Georgia", 14, QFont.Bold))
        self.round_label.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
        top_bar.addWidget(self.round_label)
        top_bar.addStretch()
        self.score_label = QLabel("Score: 0")
        self.score_label.setFont(QFont("Georgia", 14))
        self.score_label.setStyleSheet(f"color: {C.TEXT_LIGHT}; background: transparent;")
        top_bar.addWidget(self.score_label)
        root.addLayout(top_bar)
        root.addWidget(Divider())

        # Bonus suit
        bonus_row = QHBoxLayout()
        bonus_row.setAlignment(Qt.AlignCenter)
        bonus_row.setSpacing(12)
        bonus_title = QLabel("Bonus Suit:")
        bonus_title.setFont(QFont("Arial", 11))
        bonus_title.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        bonus_row.addWidget(bonus_title)
        self.bonus_symbol = QLabel("?")
        self.bonus_symbol.setFont(QFont("Arial", 22))
        self.bonus_symbol.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
        bonus_row.addWidget(self.bonus_symbol)
        self.bonus_name = QLabel("")
        self.bonus_name.setFont(QFont("Georgia", 13, QFont.Bold))
        self.bonus_name.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
        bonus_row.addWidget(self.bonus_name)
        bonus_desc = QLabel("— matching cards score double!")
        bonus_desc.setFont(QFont("Arial", 10))
        bonus_desc.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        bonus_row.addWidget(bonus_desc)
        root.addLayout(bonus_row)

        # Cards
        self.card_area = QHBoxLayout()
        self.card_area.setAlignment(Qt.AlignCenter)
        self.card_area.setSpacing(16)
        card_container = QWidget()
        card_container.setStyleSheet("background: transparent;")
        card_container.setLayout(self.card_area)
        root.addWidget(card_container, alignment=Qt.AlignCenter)

        # Hints
        self.hint_label = QLabel("Click cards to select them for replacement")
        self.hint_label.setFont(QFont("Arial", 10))
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        root.addWidget(self.hint_label)

        self.replace_label = QLabel("Replacements left: 3")
        self.replace_label.setFont(QFont("Arial", 11))
        self.replace_label.setAlignment(Qt.AlignCenter)
        self.replace_label.setStyleSheet(f"color: {C.TEXT_LIGHT}; background: transparent;")
        root.addWidget(self.replace_label)

        root.addWidget(Divider())

        # Buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(16)
        self.replace_btn = GoldButton("Replace Selected")
        self.replace_btn.setFixedWidth(200)
        self.replace_btn.clicked.connect(self._on_replace)
        btn_row.addWidget(self.replace_btn)
        self.stand_btn = GhostButton("Stand Pat  →")
        self.stand_btn.setFixedWidth(160)
        self.stand_btn.clicked.connect(self._on_stand)
        btn_row.addWidget(self.stand_btn)
        root.addLayout(btn_row)

        self.status_label = QLabel("")
        self.status_label.setFont(QFont("Georgia", 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
        root.addWidget(self.status_label)

        root.addStretch()

        bottom_bar = QHBoxLayout()
        self.next_btn = GoldButton("Next Round  →")
        self.next_btn.setFixedWidth(180)
        self.next_btn.clicked.connect(self._on_next_round)
        self.next_btn.hide()
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.next_btn)
        root.addLayout(bottom_bar)

    def load_game(self, player_name, total_rounds):
        self.game = Game([player_name], total_rounds=total_rounds)
        self.selected.clear()
        self._start_round()

    def _start_round(self):
        self.game.start_round()
        self.selected.clear()
        self.next_btn.hide()
        self.replace_btn.setEnabled(True)
        self.stand_btn.setEnabled(True)
        self.status_label.setText("")

        r = self.game.get_current_round()
        t = self.game.get_total_rounds()
        self.round_label.setText(f"Round {r} of {t}")

        player = self.game.get_players()[0]
        self.score_label.setText(f"Score: {player.get_total_score()}")

        bonus     = self.game.get_bonus_suit()
        suit_name = bonus[0]
        symbols   = {
            "Spades":   ("♠", C.TEXT_LIGHT),
            "Hearts":   ("♥", C.RED),
            "Diamonds": ("♦", C.RED),
            "Clubs":    ("♣", C.TEXT_LIGHT),
        }
        sym, col = symbols.get(suit_name, ("?", C.GOLD))
        self.bonus_symbol.setText(sym)
        self.bonus_symbol.setStyleSheet(f"color: {col}; background: transparent;")
        self.bonus_name.setText(suit_name)

        self._update_replacements_label()
        self._render_cards()

    def _render_cards(self):
        for i in reversed(range(self.card_area.count())):
            w = self.card_area.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.card_widgets.clear()

        player = self.game.get_players()[0]
        hand   = player.get_hand()

        for i in range(hand.size()):
            card   = hand.get_card(i)
            widget = CardWidget(card, i, self._on_card_toggle)
            if i in self.selected:
                widget.set_selected(True)
            self.card_widgets.append(widget)
            self.card_area.addWidget(widget)

    def _on_card_toggle(self, index):
        player_name = self.game.get_players()[0].get_name()
        max_left    = self.game.get_replacements_left(player_name)
        if index in self.selected:
            self.selected.discard(index)
        else:
            if len(self.selected) >= max_left:
                self.status_label.setText(
                    f"You can only replace {max_left} more card(s)."
                )
                return
            self.selected.add(index)
        self.status_label.setText("")
        self.card_widgets[index].set_selected(index in self.selected)

    def _on_replace(self):
        if not self.selected:
            self.status_label.setText("Select at least one card to replace.")
            return
        player_name = self.game.get_players()[0].get_name()
        self.game.replace_cards(player_name, list(self.selected))
        self.selected.clear()
        self._update_replacements_label()
        self._render_cards()
        self.status_label.setText("Cards replaced!")
        if self.game.get_replacements_left(player_name) == 0:
            self.replace_btn.setEnabled(False)

    def _on_stand(self):
        self._end_round()

    def _end_round(self):
        self.game.end_round()
        player = self.game.get_players()[0]
        self.score_label.setText(f"Score: {player.get_total_score()}")
        self.replace_btn.setEnabled(False)
        self.stand_btn.setEnabled(False)
        self.selected.clear()
        self._render_cards()

        if self.game.get_state() == GameState.GAME_OVER:
            # Hand off to summary screen
            self.on_summary(player)
        else:
            r_score = player.get_last_round_score()
            self.status_label.setText(
                f"Round scored: +{r_score}  |  Total: {player.get_total_score()}"
            )
            self.next_btn.setText("Next Round  →")
            self.next_btn.show()

    def _on_next_round(self):
        self._start_round()

    def _update_replacements_label(self):
        player_name = self.game.get_players()[0].get_name()
        left = self.game.get_replacements_left(player_name)
        self.replace_label.setText(f"Replacements left: {left}")


# ------------------------------------------------------------------ #
#  Main Window                                                        #
# ------------------------------------------------------------------ #
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HighSuit Card Game")
        self.setMinimumSize(900, 650)
        self.resize(1024, 720)
        self._score_manager = ScoreManager()
        self._last_player   = None
        self._last_rounds   = 3
        self._centre_on_screen()
        self._build_ui()

    def _centre_on_screen(self):
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size   = self.geometry()
        self.move(
            (screen.width()  - size.width())  // 2,
            (screen.height() - size.height()) // 2,
        )

    def _build_ui(self):
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        self.welcome_screen  = WelcomeScreen(
            on_start=self._show_setup,
            on_scores=self._show_high_scores
        )
        self.setup_screen    = SetupScreen(
            on_start_game=self._start_game,
            on_back=self._show_welcome
        )
        self.game_screen     = GameScreen(on_summary=self._show_summary)
        self.summary_screen  = SummaryScreen(
            on_play_again=self._play_again,
            on_menu=self._show_welcome,
            on_scores=self._show_high_scores
        )
        self.highscore_screen = HighScoreScreen(on_back=self._show_welcome)

        self.stack.addWidget(self.welcome_screen)   # 0
        self.stack.addWidget(self.setup_screen)     # 1
        self.stack.addWidget(self.game_screen)      # 2
        self.stack.addWidget(self.summary_screen)   # 3
        self.stack.addWidget(self.highscore_screen) # 4

        self.stack.setCurrentIndex(0)

    def _show_welcome(self):
        self.setup_screen.reset()
        self.stack.setCurrentIndex(0)

    def _show_setup(self):
        self.stack.setCurrentIndex(1)

    def _start_game(self, player_name, total_rounds):
        self._last_player = player_name
        self._last_rounds = total_rounds
        self.game_screen.load_game(player_name, total_rounds)
        self.stack.setCurrentIndex(2)

    def _show_summary(self, player):
        """Save score and show the summary screen."""
        self._score_manager.add_score(
            name          = player.get_name(),
            total_score   = player.get_total_score(),
            round_scores  = player.get_round_scores(),
            rounds_played = len(player.get_round_scores()),
        )
        self.summary_screen.load_summary(player, self._score_manager)
        self.stack.setCurrentIndex(3)

    def _play_again(self):
        self.game_screen.load_game(self._last_player, self._last_rounds)
        self.stack.setCurrentIndex(2)

    def _show_high_scores(self):
        self.highscore_screen.load_scores(self._score_manager)
        self.stack.setCurrentIndex(4)