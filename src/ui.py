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

        # VS Computer toggle
        vs_lbl = QLabel("Play Against")
        vs_lbl.setFont(QFont("Arial", 10))
        vs_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        pl.addWidget(vs_lbl)

        self.vs_computer_btn = QPushButton("🤖  Play vs Computer")
        self.vs_computer_btn.setCheckable(True)
        self.vs_computer_btn.setChecked(False)
        self.vs_computer_btn.setFixedHeight(42)
        self.vs_computer_btn.setFont(QFont("Arial", 11))
        self.vs_computer_btn.setCursor(Qt.PointingHandCursor)
        self.vs_computer_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {C.INPUT_BG};
                color: {C.TEXT_MUTED};
                border: 1px solid {C.INPUT_BORDER};
                border-radius: 6px;
                padding: 0 14px;
                text-align: left;
            }}
            QPushButton:checked {{
                background-color: #1A3A20;
                color: {C.GOLD};
                border: 1px solid {C.GOLD};
            }}
        """)
        pl.addWidget(self.vs_computer_btn)

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
        vs_computer = self.vs_computer_btn.isChecked()
        player_names = [name, "Computer"] if vs_computer else [name]
        self.on_start_game(player_names, self.rounds_spin.value())

    def reset(self):
        self.name_input.clear()
        self.rounds_spin.setValue(3)
        self.error_label.hide()
        self.vs_computer_btn.setChecked(False)


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
        # Fully clear previous content including nested layouts
        while self.panel_layout.count():
            item = self.panel_layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
            elif item.layout():
                # Clear nested layouts too
                sub = item.layout()
                while sub.count():
                    sub_item = sub.takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().setParent(None)
                        sub_item.widget().deleteLater()

        name         = player.get_name()
        total        = player.get_total_score()
        round_scores = player.get_round_scores()
        rounds       = len(round_scores)
        avg          = round(total / rounds) if rounds else 0

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
            row_widget = QWidget()
            row_widget.setStyleSheet("background: transparent; border: none;")
            row_layout = QHBoxLayout()
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_widget.setLayout(row_layout)

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
            row_layout.addWidget(r_lbl)
            row_layout.addWidget(s_lbl)
            self.panel_layout.addWidget(row_widget)

        self.panel_layout.addWidget(Divider())

        # ── Total & Avg ───────────────────────────────────────────
        total_widget = QWidget()
        total_widget.setStyleSheet("background: transparent; border: none;")
        total_layout = QHBoxLayout()
        total_layout.setContentsMargins(0, 0, 0, 0)
        total_widget.setLayout(total_layout)

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
        total_layout.addWidget(t_lbl)
        total_layout.addWidget(t_val)
        self.panel_layout.addWidget(total_widget)

        avg_widget = QWidget()
        avg_widget.setStyleSheet("background: transparent; border: none;")
        avg_layout = QHBoxLayout()
        avg_layout.setContentsMargins(0, 0, 0, 0)
        avg_widget.setLayout(avg_layout)

        a_lbl = QLabel(f"Avg per Round ({rounds} rounds)")
        a_lbl.setFont(QFont("Arial", 11))
        a_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        a_val = QLabel(str(avg))
        a_val.setFont(QFont("Georgia", 14, QFont.Bold))
        a_val.setAlignment(Qt.AlignRight)
        a_val.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        avg_layout.addWidget(a_lbl)
        avg_layout.addWidget(a_val)
        self.panel_layout.addWidget(avg_widget)

        # ── High score badge ──────────────────────────────────────
        if score_manager.is_high_score(avg):
            rank   = score_manager.get_rank(avg)
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
                ("#",          Qt.AlignLeft),
                ("Name",       Qt.AlignLeft),
                ("Avg/Round",  Qt.AlignRight),
                ("Date",       Qt.AlignRight),
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

                score_lbl = QLabel(str(entry.avg_score))
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
    """
    Card table — now with suit selection phase and computer player support.
    Flow per round:
      1. Cards dealt → player sees hand
      2. Player picks bonus suit (4 buttons)
      3. Player replaces cards (click to select)
      4. Round scored → next round or summary
    """

    SUIT_DATA = [
        ("Clubs",    "♣", C.TEXT_LIGHT, Suit.CLUBS),
        ("Diamonds", "♦", C.RED,        Suit.DIAMONDS),
        ("Hearts",   "♥", C.RED,        Suit.HEARTS),
        ("Spades",   "♠", C.TEXT_LIGHT, Suit.SPADES),
    ]

    def __init__(self, on_summary):
        super().__init__()
        self.on_summary   = on_summary
        self.game         = None
        self.card_widgets = []
        self.selected     = set()
        self._current_player_idx = 0
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT_DARK};")
        root = QVBoxLayout()
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(12)
        self.setLayout(root)

        # Top bar
        top_bar = QHBoxLayout()
        self.round_label = QLabel("Round 1 of 3")
        self.round_label.setFont(QFont("Georgia", 14, QFont.Bold))
        self.round_label.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
        top_bar.addWidget(self.round_label)
        top_bar.addStretch()
        self.player_label = QLabel("")
        self.player_label.setFont(QFont("Georgia", 13))
        self.player_label.setStyleSheet(f"color: {C.TEXT_LIGHT}; background: transparent;")
        top_bar.addWidget(self.player_label)
        top_bar.addSpacing(20)
        self.score_label = QLabel("Score: 0")
        self.score_label.setFont(QFont("Georgia", 13))
        self.score_label.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        top_bar.addWidget(self.score_label)
        root.addLayout(top_bar)
        root.addWidget(Divider())

        # Bonus suit row
        bonus_row = QHBoxLayout()
        bonus_row.setAlignment(Qt.AlignCenter)
        bonus_row.setSpacing(8)
        bonus_title = QLabel("Bonus Suit:")
        bonus_title.setFont(QFont("Arial", 11))
        bonus_title.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        bonus_row.addWidget(bonus_title)
        self.bonus_symbol = QLabel("—")
        self.bonus_symbol.setFont(QFont("Arial", 20))
        self.bonus_symbol.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
        bonus_row.addWidget(self.bonus_symbol)
        self.bonus_name = QLabel("Not chosen yet")
        self.bonus_name.setFont(QFont("Georgia", 12))
        self.bonus_name.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        bonus_row.addWidget(self.bonus_name)
        root.addLayout(bonus_row)

        # Suit picker (phase 1)
        self.suit_picker = QWidget()
        self.suit_picker.setStyleSheet("background: transparent;")
        suit_row = QHBoxLayout()
        suit_row.setAlignment(Qt.AlignCenter)
        suit_row.setSpacing(12)
        self.suit_picker.setLayout(suit_row)
        self.suit_buttons = []
        for name, symbol, colour, suit_tuple in self.SUIT_DATA:
            btn = QPushButton(f"{symbol}  {name}")
            btn.setFixedSize(130, 44)
            btn.setFont(QFont("Georgia", 12))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {C.PANEL};
                    color: {colour};
                    border: 2px solid {C.FELT_LIGHT};
                    border-radius: 8px;
                }}
                QPushButton:hover {{
                    border-color: {C.GOLD};
                    background-color: #1F4D35;
                }}
            """)
            btn.clicked.connect(lambda checked, s=suit_tuple: self._on_suit_chosen(s))
            suit_row.addWidget(btn)
            self.suit_buttons.append(btn)
        root.addWidget(self.suit_picker, alignment=Qt.AlignCenter)

        # Cards
        self.card_area = QHBoxLayout()
        self.card_area.setAlignment(Qt.AlignCenter)
        self.card_area.setSpacing(14)
        card_container = QWidget()
        card_container.setStyleSheet("background: transparent;")
        card_container.setLayout(self.card_area)
        root.addWidget(card_container, alignment=Qt.AlignCenter)

        # Suit scores hint
        self.suit_scores_label = QLabel("")
        self.suit_scores_label.setFont(QFont("Arial", 10))
        self.suit_scores_label.setAlignment(Qt.AlignCenter)
        self.suit_scores_label.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent;"
        )
        root.addWidget(self.suit_scores_label)

        # Hint & replacements
        self.hint_label = QLabel("Pick your bonus suit above")
        self.hint_label.setFont(QFont("Arial", 10))
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        root.addWidget(self.hint_label)

        self.replace_label = QLabel("")
        self.replace_label.setFont(QFont("Arial", 11))
        self.replace_label.setAlignment(Qt.AlignCenter)
        self.replace_label.setStyleSheet(
            f"color: {C.TEXT_LIGHT}; background: transparent;"
        )
        root.addWidget(self.replace_label)

        root.addWidget(Divider())

        # Action buttons
        btn_row = QHBoxLayout()
        btn_row.setAlignment(Qt.AlignCenter)
        btn_row.setSpacing(16)

        self.replace_btn = GoldButton("Replace Selected")
        self.replace_btn.setFixedWidth(200)
        self.replace_btn.clicked.connect(self._on_replace)
        self.replace_btn.setEnabled(False)
        btn_row.addWidget(self.replace_btn)

        self.stand_btn = GhostButton("Stand Pat  →")
        self.stand_btn.setFixedWidth(160)
        self.stand_btn.clicked.connect(self._on_stand)
        self.stand_btn.setEnabled(False)
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
        self.next_btn.setFixedWidth(200)
        self.next_btn.clicked.connect(self._on_next)
        self.next_btn.hide()
        bottom_bar.addStretch()
        bottom_bar.addWidget(self.next_btn)
        root.addLayout(bottom_bar)

    # ── Game loading ──────────────────────────────────────────────
    def load_game(self, player_names, total_rounds):
        self.game = Game(player_names, total_rounds=total_rounds)
        self.selected.clear()
        self._current_player_idx = 0
        self._start_round()

    # ── Round flow ────────────────────────────────────────────────
    def _start_round(self):
        self.game.start_round()
        self._current_player_idx = 0
        self._start_player_turn()

    def _start_player_turn(self):
        """Set up UI for the current player's turn."""
        self.selected.clear()
        self.next_btn.hide()
        self.status_label.setText("")
        self.suit_picker.show()
        self.replace_btn.setEnabled(False)
        self.stand_btn.setEnabled(False)

        player = self._current_player()
        r = self.game.get_current_round()
        t = self.game.get_total_rounds()
        self.round_label.setText(f"Round {r} of {t}")
        self.player_label.setText(f"👤 {player.get_name()}")
        self.score_label.setText(f"Score: {player.get_total_score()}")
        self.bonus_symbol.setText("—")
        self.bonus_name.setText("Not chosen yet")
        self.hint_label.setText("Pick your bonus suit above")
        self.replace_label.setText("")

        self._render_cards()
        self._update_suit_scores_label()

        # Computer plays automatically after a short delay
        if player.is_computer():
            self.hint_label.setText("🤖 Computer is thinking...")
            QTimer.singleShot(800, self._computer_turn)

    def _computer_turn(self):
        """Run the computer's full turn automatically."""
        player = self._current_player()
        name   = player.get_name()

        # Step 1: choose best suit
        chosen = self.game.computer_choose_suit(name)
        sym, col = self._suit_display(chosen)
        self.bonus_symbol.setText(sym)
        self.bonus_symbol.setStyleSheet(f"color: {col}; background: transparent;")
        self.bonus_name.setText(Suit.name(chosen))
        self.suit_picker.hide()

        self.status_label.setText(
            f"🤖 Computer chose {Suit.name(chosen)} as bonus suit"
        )

        # Step 2: replace cards after delay
        QTimer.singleShot(900, self._computer_replace)

    def _computer_replace(self):
        player = self._current_player()
        name   = player.get_name()
        indices = self.game.computer_replace_cards(name)
        self._render_cards()

        if indices:
            self.status_label.setText(
                f"🤖 Computer replaced {len(indices)} card(s)"
            )
        else:
            self.status_label.setText("🤖 Computer stood pat")

        # Step 3: score after delay
        QTimer.singleShot(900, self._end_player_turn)

    def _on_suit_chosen(self, suit):
        """Human player picks bonus suit."""
        player = self._current_player()
        self.game.set_bonus_suit(player.get_name(), suit)

        sym, col = self._suit_display(suit)
        self.bonus_symbol.setText(sym)
        self.bonus_symbol.setStyleSheet(f"color: {col}; background: transparent;")
        self.bonus_name.setText(Suit.name(suit))
        self.suit_picker.hide()

        self.hint_label.setText("Click cards to select them for replacement (max 4)")
        self.replace_label.setText("Replacements left: 4")
        self.replace_btn.setEnabled(True)
        self.stand_btn.setEnabled(True)
        self.status_label.setText("")

    def _on_replace(self):
        if not self.selected:
            self.status_label.setText("Select at least one card to replace.")
            return
        player_name = self._current_player().get_name()
        self.game.replace_cards(player_name, list(self.selected))
        self.selected.clear()
        self._update_replacements_label()
        self._render_cards()
        left = self.game.get_replacements_left(player_name)
        self.status_label.setText("Cards replaced!")
        if left == 0:
            self.replace_btn.setEnabled(False)
            self.status_label.setText("No replacements left.")

    def _on_stand(self):
        self._end_player_turn()

    def _end_player_turn(self):
        """Score current player, move to next player or end round."""
        player = self._current_player()
        score  = player.record_round_score()

        suit_name = Suit.name(player.get_bonus_suit()) if player.get_bonus_suit() else "?"
        self.status_label.setText(
            f"{player.get_name()} scored {score} pts  "
            f"(best suit + {'5 bonus ✓' if self._bonus_matched(player) else 'no bonus'})"
        )
        self.replace_btn.setEnabled(False)
        self.stand_btn.setEnabled(False)
        self._render_cards()

        # Advance to next player or end round
        self._current_player_idx += 1
        if self._current_player_idx < len(self.game.get_players()):
            # More players this round
            self.next_btn.setText(
                f"Next: {self.game.get_players()[self._current_player_idx].get_name()}  →"
            )
            self.next_btn.show()
        else:
            # All players done — end round properly
            self._finish_round()

    def _finish_round(self):
        """Advance game state and show next round or summary."""
        # end_round() just advances state — scoring already done per player
        # We call it manually here to move GameState
        self.game._state = __import__('src.game', fromlist=['GameState']).GameState.REPLACING
        self.game.end_round()

        if self.game.get_state() == __import__('src.game', fromlist=['GameState']).GameState.GAME_OVER:
            # Trigger summary via on_summary callback
            # Pass the human (non-computer) player
            human = self._get_human_player()
            self.on_summary(human)
        else:
            self.next_btn.setText("Next Round  →")
            self.next_btn.show()

    def _on_next(self):
        if self._current_player_idx < len(self.game.get_players()):
            # Next player this round
            self._start_player_turn()
        else:
            # Next round
            self._current_player_idx = 0
            self._start_round()

    # ── Helpers ───────────────────────────────────────────────────
    def _current_player(self):
        idx = min(self._current_player_idx, len(self.game.get_players()) - 1)
        return self.game.get_players()[idx]

    def _get_human_player(self):
        for p in self.game.get_players():
            if not p.is_computer():
                return p
        return self.game.get_players()[0]

    def _bonus_matched(self, player):
        hand      = player.get_hand()
        bonus_idx = Suit.index(player.get_bonus_suit()) if player.get_bonus_suit() else -1
        best_idx  = hand.best_suit_index()
        return best_idx == bonus_idx

    def _suit_display(self, suit):
        symbols = {
            "Clubs":    ("♣", C.TEXT_LIGHT),
            "Hearts":   ("♥", C.RED),
            "Diamonds": ("♦", C.RED),
            "Spades":   ("♠", C.TEXT_LIGHT),
        }
        return symbols.get(Suit.name(suit), ("?", C.GOLD))

    def _update_suit_scores_label(self):
        player = self._current_player()
        scores = player.get_hand().suit_scores()
        symbols = {"Clubs": "♣", "Diamonds": "♦", "Hearts": "♥", "Spades": "♠"}
        parts = []
        for suit in Suit.ALL:
            idx = Suit.index(suit)
            if idx in scores:
                sym = symbols[Suit.name(suit)]
                parts.append(f"{sym} {Suit.name(suit)}: {scores[idx]}")
        self.suit_scores_label.setText("   |   ".join(parts))

    def _render_cards(self):
        for i in reversed(range(self.card_area.count())):
            w = self.card_area.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.card_widgets.clear()

        player = self._current_player()
        hand   = player.get_hand()

        for i in range(hand.size()):
            card   = hand.get_card(i)
            widget = CardWidget(card, i, self._on_card_toggle)
            if i in self.selected:
                widget.set_selected(True)
            self.card_widgets.append(widget)
            self.card_area.addWidget(widget)

    def _on_card_toggle(self, index):
        player_name = self._current_player().get_name()
        max_left    = self.game.get_replacements_left(player_name)
        if index in self.selected:
            self.selected.discard(index)
        else:
            if len(self.selected) >= max_left:
                self.status_label.setText(f"Max {max_left} replacement(s).")
                return
            self.selected.add(index)
        self.status_label.setText("")
        self.card_widgets[index].set_selected(index in self.selected)

    def _update_replacements_label(self):
        player_name = self._current_player().get_name()
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
        self._last_players  = ["Player"]
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

    def _start_game(self, player_names, total_rounds):
        self._last_players = player_names
        self._last_rounds  = total_rounds
        self.game_screen.load_game(player_names, total_rounds)
        self.stack.setCurrentIndex(2)

    def _show_summary(self, player):
        """Save score and show the summary screen."""
        # Save BEFORE loading summary so rank is calculated correctly
        self._score_manager.add_score(
            name          = player.get_name(),
            total_score   = player.get_total_score(),
            round_scores  = player.get_round_scores(),
            rounds_played = len(player.get_round_scores()),
        )
        self.summary_screen.load_summary(player, self._score_manager)
        self.stack.setCurrentIndex(3)

    def _play_again(self):
        self.game_screen.load_game(self._last_players, self._last_rounds)
        self.stack.setCurrentIndex(2)

    def _show_high_scores(self):
        self.highscore_screen.load_scores(self._score_manager)
        self.stack.setCurrentIndex(4)