from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QLineEdit,
    QSpinBox, QFrame, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

from src.game import Game, GameState
from src.card import Suit
from src.scores import ScoreManager
from src.sound import SoundManager

# Global sound manager — one instance for the whole app
_SFX = SoundManager()


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
class _Divider(QFrame):
    """Internal horizontal rule."""
    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background-color: {C.FELT_LIGHT}; border: none;")


class _Row(QWidget):
    """A single left+right label row — no layout leak possible."""
    def __init__(self, left, right, bold=False, colour=None):
        super().__init__()
        self.setStyleSheet("background: transparent;")
        lay = QHBoxLayout()
        lay.setContentsMargins(0, 2, 0, 2)
        self.setLayout(lay)

        colour = colour or C.TEXT_LIGHT
        weight = QFont.Bold if bold else QFont.Normal

        l_lbl = QLabel(left)
        l_lbl.setFont(QFont("Georgia", 12, weight))
        l_lbl.setStyleSheet(f"color: {colour}; background: transparent;")

        r_lbl = QLabel(right)
        r_lbl.setFont(QFont("Georgia", 12, weight))
        r_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        r_lbl.setStyleSheet(f"color: {colour}; background: transparent;")

        lay.addWidget(l_lbl)
        lay.addWidget(r_lbl)




class GoldButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(48)
        self.setFont(QFont("Georgia", 12, QFont.Bold))
        self.setCursor(Qt.PointingHandCursor)
        self._apply_style()
        # Play click sound on every press automatically
        self.clicked.connect(lambda: _SFX.play("click"))

    def _apply_style(self):
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
        # Play click sound on every press automatically
        self.clicked.connect(lambda: _SFX.play("click"))


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


# Aliases so both names work
_Divider = Divider


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


        mute_btn = GhostButton("🔇  Mute Music")
        mute_btn.setFixedWidth(180)
        mute_btn.setCheckable(True)
        mute_btn.toggled.connect(lambda checked: (
            _SFX.toggle_music(),
            mute_btn.setText("🔊  Unmute Music" if checked else "🔇  Mute Music")
        ))
        root.addWidget(mute_btn, alignment=Qt.AlignCenter)

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
    """
    Setup flow:
    - 1 Player: show name input + optional "Play vs Computer" toggle
    - 2 Players: show two name inputs, no computer option
    """
    def __init__(self, on_start_game, on_back):
        super().__init__()
        self.on_start_game = on_start_game
        self.on_back       = on_back
        self._num_players  = 1
        self._vs_computer  = False
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet(f"background-color: {C.FELT};")
        root = QVBoxLayout()
        root.setAlignment(Qt.AlignCenter)
        self.setLayout(root)

        panel = QWidget()
        panel.setFixedWidth(440)
        panel.setStyleSheet(f"""
            background-color: {C.PANEL};
            border-radius: 12px;
            border: 1px solid {C.FELT_LIGHT};
        """)
        self.pl = QVBoxLayout()
        self.pl.setContentsMargins(36, 36, 36, 36)
        self.pl.setSpacing(14)
        panel.setLayout(self.pl)

        # Title
        title = QLabel("New Game")
        title.setFont(QFont("Georgia", 22, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(
            f"color: {C.GOLD}; background: transparent; border: none;"
        )
        self.pl.addWidget(title)
        self.pl.addWidget(Divider())

        # ── Number of players ─────────────────────────────────────
        np_lbl = QLabel("Number of Players")
        np_lbl.setFont(QFont("Arial", 10))
        np_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        self.pl.addWidget(np_lbl)

        np_row = QHBoxLayout()
        np_row.setSpacing(10)
        self.btn_1p = QPushButton("1 Player")
        self.btn_2p = QPushButton("2 Players")
        for btn in [self.btn_1p, self.btn_2p]:
            btn.setFixedHeight(40)
            btn.setFont(QFont("Georgia", 11))
            btn.setCheckable(True)
            btn.setCursor(Qt.PointingHandCursor)
        self.btn_1p.setChecked(True)
        self.btn_1p.clicked.connect(lambda: self._set_num_players(1))
        self.btn_2p.clicked.connect(lambda: self._set_num_players(2))
        self._style_player_btns()

        np_container = QWidget()
        np_container.setStyleSheet("background: transparent; border: none;")
        np_container.setLayout(np_row)
        np_row.addWidget(self.btn_1p)
        np_row.addWidget(self.btn_2p)
        self.pl.addWidget(np_container)

        # ── Number of rounds ──────────────────────────────────────
        rounds_lbl = QLabel("Number of Rounds (1–3)")
        rounds_lbl.setFont(QFont("Arial", 10))
        rounds_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        self.pl.addWidget(rounds_lbl)

        self.rounds_spin = QSpinBox()
        self.rounds_spin.setRange(1, 3)
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
        self.pl.addWidget(self.rounds_spin)

        # ── Player 1 name ─────────────────────────────────────────
        self.p1_lbl = QLabel("Your Name")
        self.p1_lbl.setFont(QFont("Arial", 10))
        self.p1_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        self.pl.addWidget(self.p1_lbl)

        self.name1_input = StyledInput(placeholder="Enter your name...")
        self.name1_input.setMaxLength(20)
        self.pl.addWidget(self.name1_input)

        # ── VS Computer toggle (1 player only) ───────────────────
        self.vs_computer_btn = QPushButton("🤖  Play vs Computer")
        self.vs_computer_btn.setCheckable(True)
        self.vs_computer_btn.setChecked(False)
        self.vs_computer_btn.setFixedHeight(42)
        self.vs_computer_btn.setFont(QFont("Arial", 11))
        self.vs_computer_btn.setCursor(Qt.PointingHandCursor)
        self.vs_computer_btn.setStyleSheet(self._computer_btn_style(False))
        self.vs_computer_btn.toggled.connect(self._on_computer_toggled)
        self.pl.addWidget(self.vs_computer_btn)

        # ── Player 2 name (2 player mode only) ───────────────────
        self.p2_lbl = QLabel("Player 2 Name")
        self.p2_lbl.setFont(QFont("Arial", 10))
        self.p2_lbl.setStyleSheet(
            f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
        )
        self.pl.addWidget(self.p2_lbl)

        self.name2_input = StyledInput(placeholder="Enter Player 2's name...")
        self.name2_input.setMaxLength(20)
        self.pl.addWidget(self.name2_input)

        self.pl.addWidget(Divider())

        # Error
        self.error_label = QLabel("")
        self.error_label.setFont(QFont("Arial", 10))
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setStyleSheet(
            f"color: {C.RED}; background: transparent; border: none;"
        )
        self.error_label.hide()
        self.pl.addWidget(self.error_label)

        start_btn = GoldButton("Start Game  →")
        start_btn.clicked.connect(self._on_start_clicked)
        self.pl.addWidget(start_btn)

        back_btn = GhostButton("← Back to Menu")
        back_btn.clicked.connect(self.on_back)
        self.pl.addWidget(back_btn)

        root.addWidget(panel, alignment=Qt.AlignCenter)

        # Start in 1-player mode
        self._set_num_players(1)

    def _computer_btn_style(self, active):
        return f"""
            QPushButton {{
                background-color: {'#1A3A20' if active else C.INPUT_BG};
                color: {C.GOLD if active else C.TEXT_MUTED};
                border: {'2px solid ' + C.GOLD if active else '1px solid ' + C.INPUT_BORDER};
                border-radius: 6px;
                padding: 0 14px;
                text-align: center;
            }}
            QPushButton:hover {{
                border-color: {C.GOLD};
                color: {C.GOLD};
            }}
        """

    def _on_computer_toggled(self, checked):
        self._vs_computer = checked
        self.vs_computer_btn.setStyleSheet(self._computer_btn_style(checked))

    def _set_num_players(self, n):
        self._num_players = n
        self._vs_computer = False
        self.btn_1p.setChecked(n == 1)
        self.btn_2p.setChecked(n == 2)
        self._style_player_btns()

        # 1 player: show computer toggle, hide p2 name
        # 2 players: hide computer toggle, show p2 name
        self.vs_computer_btn.setVisible(n == 1)
        self.vs_computer_btn.setChecked(False)
        self.p1_lbl.setText("Your Name" if n == 1 else "Player 1 Name")
        self.p2_lbl.setVisible(n == 2)
        self.name2_input.setVisible(n == 2)
        self.error_label.hide()

    def _style_player_btns(self):
        for btn, active in [
            (self.btn_1p, self._num_players == 1),
            (self.btn_2p, self._num_players == 2),
        ]:
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {'#1A3A20' if active else C.INPUT_BG};
                    color: {C.GOLD if active else C.TEXT_MUTED};
                    border: {'2px solid ' + C.GOLD if active else '1px solid ' + C.INPUT_BORDER};
                    border-radius: 6px;
                    padding: 0 14px;
                }}
                QPushButton:hover {{
                    border-color: {C.GOLD};
                    color: {C.GOLD};
                }}
            """)

    def _on_start_clicked(self):
        name1 = self.name1_input.text().strip()
        if not name1:
            self.error_label.setText("Please enter your name.")
            self.error_label.show()
            return

        if self._num_players == 1:
            if self._vs_computer:
                player_names = [name1, "Computer"]
            else:
                player_names = [name1]

        else:  # 2 players
            name2 = self.name2_input.text().strip()
            if not name2:
                self.error_label.setText("Please enter Player 2's name.")
                self.error_label.show()
                return
            if name1.lower() == name2.lower():
                self.error_label.setText("Players must have different names.")
                self.error_label.show()
                return
            player_names = [name1, name2]

        self.error_label.hide()
        self.on_start_game(player_names, self.rounds_spin.value())

    def reset(self):
        self.name1_input.clear()
        self.name2_input.clear()
        self.rounds_spin.setValue(3)
        self.error_label.hide()
        self._set_num_players(1)


# ------------------------------------------------------------------ #
#  Summary Screen                                                     #
# ------------------------------------------------------------------ #
class SummaryScreen(QWidget):
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
        root.setContentsMargins(0, 20, 0, 0)
        self.setLayout(root)

        # Scroll area so content never overflows
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setFixedWidth(500)
        self.scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #0D2B20;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #2D6A4F;
                border-radius: 3px;
            }
        """)
        root.addWidget(self.scroll, alignment=Qt.AlignCenter)

    def load_summary(self, players, rounds_played, score_manager):
        """Rebuild content from scratch into a fresh widget — no clear bugs."""

        # Fresh inner widget every time — no deleteLater needed
        inner = QWidget()
        inner.setStyleSheet(f"background-color: {C.PANEL}; border-radius: 12px;")
        layout = QVBoxLayout()
        layout.setContentsMargins(36, 32, 36, 32)
        layout.setSpacing(12)
        inner.setLayout(layout)

        sorted_players = sorted(
            players, key=lambda p: p.get_total_score(), reverse=True
        )
        winner = sorted_players[0]

        # ── Trophy ────────────────────────────────────────────────
        trophy = QLabel("🏆")
        trophy.setFont(QFont("Arial", 36))
        trophy.setAlignment(Qt.AlignCenter)
        trophy.setStyleSheet("background: transparent;")
        layout.addWidget(trophy)

        # ── Winner title ──────────────────────────────────────────
        title = QLabel(f"{winner.get_name()} Wins!")
        title.setFont(QFont("Georgia", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
        layout.addWidget(title)

        layout.addWidget(_Divider())

        # ── Final scores ──────────────────────────────────────────
        fs_lbl = QLabel("FINAL SCORES")
        fs_lbl.setFont(QFont("Arial", 9))
        fs_lbl.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        layout.addWidget(fs_lbl)

        for player in sorted_players:
            is_winner = (player == winner)
            row = _Row(
                left  = f"{'👑 ' if is_winner else '   '}{player.get_name()}",
                right = f"{player.get_total_score()} pts",
                bold  = is_winner,
                colour= C.GOLD if is_winner else C.TEXT_LIGHT,
            )
            layout.addWidget(row)

        layout.addWidget(_Divider())

        # ── Round breakdown ───────────────────────────────────────
        bd_lbl = QLabel("ROUND BREAKDOWN")
        bd_lbl.setFont(QFont("Arial", 9))
        bd_lbl.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")
        layout.addWidget(bd_lbl)

        for player in sorted_players:
            p_hdr = QLabel(player.get_name())
            p_hdr.setFont(QFont("Georgia", 11, QFont.Bold))
            p_hdr.setStyleSheet(f"color: {C.TEXT_LIGHT}; background: transparent;")
            layout.addWidget(p_hdr)

            for i, score in enumerate(player.get_round_scores(), 1):
                row = _Row(
                    left   = f"    Round {i}",
                    right  = f"+{score}",
                    colour = C.GOLD,
                )
                layout.addWidget(row)

        layout.addWidget(_Divider())

        # ── High score badges ─────────────────────────────────────
        for player in sorted_players:
            avg = round(player.get_total_score() / rounds_played, 2)
            if score_manager.is_high_score(avg):
                rank   = score_manager.get_rank(avg)
                hs_lbl = QLabel(f"🎉  {player.get_name()} — New High Score! Rank #{rank}")
                hs_lbl.setFont(QFont("Georgia", 10, QFont.Bold))
                hs_lbl.setAlignment(Qt.AlignCenter)
                hs_lbl.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
                layout.addWidget(hs_lbl)

        layout.addWidget(_Divider())

        # ── Buttons ───────────────────────────────────────────────
        play_btn = GoldButton("Play Again")
        play_btn.clicked.connect(self.on_play_again)
        layout.addWidget(play_btn)

        scores_btn = GhostButton("🏆  View High Scores")
        scores_btn.clicked.connect(self.on_scores)
        layout.addWidget(scores_btn)

        menu_btn = GhostButton("← Main Menu")
        menu_btn.clicked.connect(self.on_menu)
        layout.addWidget(menu_btn)

        self.scroll.setWidget(inner)


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
                # Use a QWidget row instead of bare QHBoxLayout
                # This prevents stylesheet bleed causing strikethrough
                row_widget = QWidget()
                row_widget.setStyleSheet("background: transparent; border: none;")
                row_layout = QHBoxLayout()
                row_layout.setContentsMargins(0, 4, 0, 4)
                row_layout.setSpacing(8)
                row_widget.setLayout(row_layout)

                # Rank — fixed width, medal emoji or number
                medal = self.MEDALS.get(i)
                rank_lbl = QLabel(medal if medal else str(i))
                rank_lbl.setFixedWidth(36)
                rank_lbl.setFont(QFont("Arial", 14 if medal else 12))
                rank_lbl.setAlignment(Qt.AlignCenter)
                rank_lbl.setStyleSheet(
                    f"color: {C.GOLD}; background: transparent; border: none;"
                )
                row_layout.addWidget(rank_lbl)

                # Name — stretches to fill
                name_lbl = QLabel(entry.name)
                name_lbl.setFont(QFont("Georgia", 12))
                name_lbl.setStyleSheet(
                    f"color: {C.TEXT_LIGHT}; background: transparent; border: none;"
                )
                row_layout.addWidget(name_lbl, stretch=2)

                # Avg score
                score_lbl = QLabel(f"{entry.avg_score:.1f}")
                score_lbl.setFont(QFont("Georgia", 13, QFont.Bold))
                score_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                score_lbl.setFixedWidth(60)
                score_lbl.setStyleSheet(
                    f"color: {C.GOLD}; background: transparent; border: none;"
                )
                row_layout.addWidget(score_lbl)

                # Date
                date_lbl = QLabel(entry.date)
                date_lbl.setFont(QFont("Arial", 9))
                date_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
                date_lbl.setFixedWidth(90)
                date_lbl.setStyleSheet(
                    f"color: {C.TEXT_MUTED}; background: transparent; border: none;"
                )
                row_layout.addWidget(date_lbl)

                self.panel_layout.addWidget(row_widget)

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

        self.score_hand_btn = GoldButton("Score My Hand  ✓")
        self.score_hand_btn.setFixedWidth(200)
        self.score_hand_btn.clicked.connect(self._end_player_turn)
        self.score_hand_btn.hide()
        btn_row.addWidget(self.score_hand_btn)

        

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
        self.score_hand_btn.hide()

        player = self._current_player()
        r = self.game.get_current_round()
        t = self.game.get_total_rounds()

        # Clear round + player labels
        self.round_label.setText(f"Round {r} of {t}")
        self.player_label.setText(f"👤 {player.get_name()}'s Turn")
        self.score_label.setText(f"Score: {player.get_total_score()}")

        # Reset bonus suit display
        self.bonus_symbol.setText("—")
        self.bonus_symbol.setStyleSheet(f"color: {C.GOLD}; background: transparent;")
        self.bonus_name.setText("Not chosen yet")

        self.hint_label.setText(
            f"👆 {player.get_name()}, pick your bonus suit"
        )
        self.replace_label.setText("")
        self._update_suit_scores_label()
        self._render_cards()

        if player.is_computer():
            self.hint_label.setText("🤖 Computer is thinking...")
            QTimer.singleShot(900, self._computer_turn)

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
        """Human player picks bonus suit. Now they get ONE replacement action."""
        player = self._current_player()
        self.game.set_bonus_suit(player.get_name(), suit)
        _SFX.play("suit")

        sym, col = self._suit_display(suit)
        self.bonus_symbol.setText(sym)
        self.bonus_symbol.setStyleSheet(f"color: {col}; background: transparent;")
        self.bonus_name.setText(Suit.name(suit))
        self.suit_picker.hide()

        self.hint_label.setText("Select up to 4 cards to replace — you get one replacement action")
        self.replace_label.setText("You have 1 replacement action remaining")
        _SFX.play("click")
        self.replace_btn.setEnabled(True)
        self.score_hand_btn.hide()
        self.status_label.setText("")

    def _on_replace(self):
        """Replace selected cards — single action, then show Score button."""
        if not self.selected:
            self.status_label.setText("Select at least one card to replace.")
            return
        player_name = self._current_player().get_name()
        self.game.replace_cards(player_name, list(self.selected))
        _SFX.play("replace")
        self.selected.clear()
        self.replace_btn.setEnabled(False)
        self._render_cards()
        self.status_label.setText("Cards replaced!")
        self.hint_label.setText("Happy with your hand?")
        self.replace_label.setText("")
        self.score_hand_btn.show()



    def _end_player_turn(self):
        player = self._current_player()
        name   = player.get_name()
        score  = self.game.score_player(name)
        bonus_matched = self._bonus_matched(player)
        _SFX.play("score")

        self.replace_btn.setEnabled(False)
        self.score_hand_btn.hide()
        self._render_cards()

        bonus_txt = "  (+5 bonus ✓)" if bonus_matched else ""
        self.status_label.setText(
            f"✅ {name} scored {score} pts this round{bonus_txt}  |  "
            f"Total: {player.get_total_score()}"
        )

        self._current_player_idx += 1
        players = self.game.get_players()

        if self._current_player_idx < len(players):
            next_name = players[self._current_player_idx].get_name()
            self.hint_label.setText("")
            self.next_btn.setText(f"▶  {next_name}'s Turn  →")
            self.next_btn.show()
        else:
            self._finish_round()


    def _finish_round(self):
        self.game.advance_round_state()
        if self.game.get_state() == GameState.GAME_OVER:
            _SFX.play("win")
            self.on_summary(self.game.get_players())
        else:
            r = self.game.get_current_round()
            t = self.game.get_total_rounds()
            self.round_label.setText(f"Round {r} of {t} — Complete!")
            self.next_btn.setText(f"▶  Start Round {r + 1}  →")
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
        _SFX.play("card")

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
        _SFX.start_music()

    def _centre_on_screen(self):
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        size   = self.geometry()
        self.move(
            (screen.width()  - size.width())  // 2,
            (screen.height() - size.height()) // 2,
        )

    def _build_ui(self):
        # Root widget holds stack + footer
        root_widget = QWidget()
        root_layout = QVBoxLayout()
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        root_widget.setLayout(root_layout)
        self.setCentralWidget(root_widget)

        self.stack = QStackedWidget()
        root_layout.addWidget(self.stack)

        # ── Persistent footer ─────────────────────────────────────
        footer = QWidget()
        footer.setFixedHeight(26)
        footer.setStyleSheet(f"background-color: {C.FELT_DARK};")
        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(12, 0, 12, 0)
        footer.setLayout(footer_layout)

        footer_text = QLabel("Built by ")
        footer_text.setFont(QFont("Arial", 8))
        footer_text.setStyleSheet(f"color: {C.TEXT_MUTED}; background: transparent;")

        footer_link = QLabel('<a href="https://github.com/Sunnah25" style="color: #D4A843; text-decoration: none;">Mohius Sunnah Chowdhury</a>')
        footer_link.setFont(QFont("Arial", 8))
        footer_link.setStyleSheet("background: transparent;")
        footer_link.setOpenExternalLinks(True)
        footer_link.setCursor(Qt.PointingHandCursor)

        footer_layout.addStretch()
        footer_layout.addWidget(footer_text)
        footer_layout.addWidget(footer_link)
        footer_layout.addStretch()

        root_layout.addWidget(footer)

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

    def _show_summary(self, players):
        """
        Save scores for ALL players (including Computer — matches Java).
        Then show summary with winner declared.
        """
        rounds_played = self._last_rounds
        for player in players:
            self._score_manager.add_score(
                name          = player.get_name(),
                total_score   = player.get_total_score(),
                rounds_played = rounds_played,
            )
        self.summary_screen.load_summary(players, rounds_played, self._score_manager)
        self.stack.setCurrentIndex(3)

    def _play_again(self):
        self.game_screen.load_game(self._last_players, self._last_rounds)
        self.stack.setCurrentIndex(2)

    def _show_high_scores(self):
        self.highscore_screen.load_scores(self._score_manager)
        self.stack.setCurrentIndex(4)