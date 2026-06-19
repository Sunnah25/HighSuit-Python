from src.deck import Deck
from src.player import Player
from src.card import Suit


class GameState:
    WAITING   = "waiting"
    DEALING   = "dealing"
    CHOOSING_SUIT = "choosing_suit"   # Player picks bonus suit
    REPLACING = "replacing"           # Player swaps cards
    SCORING   = "scoring"
    GAME_OVER = "game_over"


class Game:
    """
    HighSuit game engine.

    Rules (matching Java original):
    - Player CHOOSES their bonus suit after seeing their hand
    - Score = highest single-suit card total
    - +5 bonus if that suit matches chosen bonus suit
    - Card values: 2-9 face value, 10/J/Q/K=10, Ace=11
    - Up to 4 cards can be replaced per round
    - Computer player: picks best suit, drops all non-matching cards
    """

    MAX_REPLACEMENTS = 4
    MAX_ROUNDS       = 3

    def __init__(self, player_names, total_rounds=3):
        if not player_names:
            raise ValueError("At least one player name required.")
        if not (1 <= total_rounds <= self.MAX_ROUNDS):
            raise ValueError("Rounds must be 1–3.")

        self._players       = [Player(name) for name in player_names]
        self._deck          = Deck()
        self._total_rounds  = total_rounds
        self._current_round = 0
        self._state         = GameState.WAITING
        self._replacements_used = {p.get_name(): 0 for p in self._players}
        self._current_player_index = 0

    # ── Getters ──────────────────────────────────────────────────
    def get_players(self):
        return list(self._players)

    def get_player(self, name):
        for p in self._players:
            if p.get_name() == name:
                return p
        return None

    def get_current_round(self):
        return self._current_round

    def get_total_rounds(self):
        return self._total_rounds

    def get_state(self):
        return self._state

    def get_replacements_used(self, player_name):
        return self._replacements_used.get(player_name, 0)

    def get_replacements_left(self, player_name):
        used = self._replacements_used.get(player_name, 0)
        return max(0, self.MAX_REPLACEMENTS - used)

    def get_winner(self):
        if self._state != GameState.GAME_OVER:
            return None
        return max(self._players, key=lambda p: p.get_total_score())

    def get_leaderboard(self):
        return sorted(
            self._players, key=lambda p: p.get_total_score(), reverse=True
        )

    def get_current_player(self):
        return self._players[self._current_player_index]

    # ── Round flow ────────────────────────────────────────────────
    def start_round(self):
        """Deal 5 cards to all players. Ready for suit selection."""
        if self._state == GameState.GAME_OVER:
            raise RuntimeError("Game is over.")

        self._current_round += 1
        self._deck.reset()
        self._current_player_index = 0
        self._state = GameState.DEALING

        for name in self._replacements_used:
            self._replacements_used[name] = 0

        for player in self._players:
            player.clear_hand()
            player.add_cards(self._deck.deal_many(5))

        self._state = GameState.CHOOSING_SUIT

    def set_bonus_suit(self, player_name, suit):
        """
        Player nominates their bonus suit for this round.
        suit must be one of Suit.ALL tuples.
        """
        if self._state != GameState.CHOOSING_SUIT:
            raise RuntimeError("Not time to choose bonus suit.")
        player = self.get_player(player_name)
        if not player:
            raise ValueError(f"No player '{player_name}'.")
        player.set_bonus_suit(suit)
        self._state = GameState.REPLACING

    def computer_choose_suit(self, player_name):
        """
        Computer automatically picks the suit with highest
        current card total as bonus suit.
        Returns the chosen suit tuple.
        """
        player = self.get_player(player_name)
        best_idx  = player.get_hand().best_suit_index()
        best_suit = Suit.from_index(best_idx)
        player.set_bonus_suit(best_suit)
        self._state = GameState.REPLACING
        return best_suit

    def computer_replace_cards(self, player_name):
        """
        Computer drops all cards NOT in its bonus suit.
        Keeps at least 1 card (avoids dropping everything).
        Returns list of indices replaced.
        """
        player     = self.get_player(player_name)
        bonus_suit = player.get_bonus_suit()
        bonus_idx  = Suit.index(bonus_suit)
        hand       = player.get_hand()

        drop_indices = [
            i for i in range(hand.size())
            if hand.get_card(i).get_suit_index() != bonus_idx
        ]

        # Never drop all cards — keep at least 1
        if len(drop_indices) >= hand.size():
            drop_indices = drop_indices[:hand.size() - 1]

        # Cap at MAX_REPLACEMENTS
        drop_indices = drop_indices[:self.MAX_REPLACEMENTS]

        new_cards = []
        for idx in drop_indices:
            new_card = self._deck.deal()
            if new_card:
                player.replace_card(idx, new_card)
                new_cards.append((idx, new_card))

        self._replacements_used[player_name] = len(drop_indices)
        return drop_indices

    def replace_cards(self, player_name, indices):
        """Human player replaces cards at given indices."""
        if self._state != GameState.REPLACING:
            raise RuntimeError("Not time to replace cards.")

        player  = self.get_player(player_name)
        indices = list(set(indices))

        if any(i < 0 or i >= 5 for i in indices):
            raise ValueError("Indices must be 0–4.")

        remaining = self.get_replacements_left(player_name)
        if len(indices) > remaining:
            raise ValueError(
                f"Only {remaining} replacement(s) left."
            )

        new_cards = []
        for idx in sorted(indices):
            card = self._deck.deal()
            if card:
                player.replace_card(idx, card)
                new_cards.append(card)

        self._replacements_used[player_name] += len(new_cards)
        return new_cards

    def end_round(self):
        """Score all players. Advance state."""
        if self._state != GameState.REPLACING:
            raise RuntimeError("Cannot end round now.")

        self._state = GameState.SCORING
        scores = {}
        for player in self._players:
            score = player.record_round_score()
            scores[player.get_name()] = score

        if self._current_round >= self._total_rounds:
            self._state = GameState.GAME_OVER
        else:
            self._state = GameState.WAITING

        return scores

    def reset_game(self):
        for player in self._players:
            player.reset()
        self._deck.reset()
        self._current_round = 0
        self._state         = GameState.WAITING
        self._replacements_used = {p.get_name(): 0 for p in self._players}
        self._current_player_index = 0

    def __repr__(self):
        return (
            f"Game(round={self._current_round}/{self._total_rounds}, "
            f"state={self._state})"
        )