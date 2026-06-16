import random
from src.deck import Deck
from src.player import Player
from src.card import Suit


class GameState:
    """All possible states the game can be in at any point."""
    WAITING    = "waiting"     # Not started yet
    DEALING    = "dealing"     # Cards being dealt
    REPLACING  = "replacing"   # Player choosing cards to replace
    SCORING    = "scoring"     # Round being scored
    GAME_OVER  = "game_over"   # All rounds complete


class Game:
    """
    Core game engine for HighSuit.

    Rules:
    - Each game has a fixed number of rounds (default 3).
    - At the start of each round a random bonus suit is chosen.
    - Each player is dealt 5 cards.
    - Players may replace up to MAX_REPLACEMENTS cards once per round.
    - Cards matching the bonus suit score double their rank value.
    - The player with the highest total score after all rounds wins.
    """

    MAX_REPLACEMENTS = 3
    DEFAULT_ROUNDS   = 3

    def __init__(self, player_names, total_rounds=DEFAULT_ROUNDS):
        if not player_names:
            raise ValueError("At least one player name is required.")
        if total_rounds < 1:
            raise ValueError("Game must have at least 1 round.")

        self._players      = [Player(name) for name in player_names]
        self._deck         = Deck()
        self._total_rounds = total_rounds
        self._current_round = 0
        self._bonus_suit   = None
        self._state        = GameState.WAITING
        self._replacements_used = {p.get_name(): 0 for p in self._players}

    # ------------------------------------------------------------------ #
    #  Getters                                                             #
    # ------------------------------------------------------------------ #

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

    def get_bonus_suit(self):
        return self._bonus_suit

    def get_state(self):
        return self._state

    def get_replacements_used(self, player_name):
        return self._replacements_used.get(player_name, 0)

    def get_replacements_left(self, player_name):
        used = self._replacements_used.get(player_name, 0)
        return max(0, self.MAX_REPLACEMENTS - used)

    def get_winner(self):
        """Return the player with the highest total score. Call after game over."""
        if self._state != GameState.GAME_OVER:
            return None
        return max(self._players, key=lambda p: p.get_total_score())

    def get_leaderboard(self):
        """Return players sorted by total score descending."""
        return sorted(self._players, key=lambda p: p.get_total_score(), reverse=True)

    # ------------------------------------------------------------------ #
    #  Game Flow                                                           #
    # ------------------------------------------------------------------ #

    def start_round(self):
        """
        Begin a new round:
        - Increment round counter
        - Reset deck and shuffle
        - Pick a random bonus suit
        - Deal 5 cards to each player
        """
        if self._state == GameState.GAME_OVER:
            raise RuntimeError("Game is already over. Start a new game.")

        self._current_round += 1
        self._deck.reset()
        self._bonus_suit = random.choice(Suit.ALL)
        self._state = GameState.DEALING

        # Reset replacement counters for this round
        for name in self._replacements_used:
            self._replacements_used[name] = 0

        # Deal 5 cards to each player
        for player in self._players:
            player.clear_hand()
            player.add_cards(self._deck.deal_many(5))

        self._state = GameState.REPLACING

    def replace_cards(self, player_name, indices):
        """
        Replace cards at the given indices for a player.

        - indices: list of 0-based positions in hand to replace (max 3 total)
        - Each replaced card is drawn from the deck
        - Returns the list of new cards dealt
        """
        if self._state != GameState.REPLACING:
            raise RuntimeError("Card replacement is not allowed right now.")

        player = self.get_player(player_name)
        if player is None:
            raise ValueError(f"No player named '{player_name}'.")

        # Deduplicate and validate indices
        indices = list(set(indices))
        if any(i < 0 or i >= 5 for i in indices):
            raise ValueError("Card indices must be between 0 and 4.")

        remaining = self.get_replacements_left(player_name)
        if len(indices) > remaining:
            raise ValueError(
                f"Cannot replace {len(indices)} cards. "
                f"{player_name} has {remaining} replacement(s) left."
            )

        new_cards = []
        for index in sorted(indices):
            new_card = self._deck.deal()
            if new_card is None:
                break
            player.replace_card(index, new_card)
            new_cards.append(new_card)

        self._replacements_used[player_name] += len(new_cards)
        return new_cards

    def end_round(self):
        """
        Score the round for all players.
        Returns a dict of {player_name: round_score}.
        If all rounds are done, sets state to GAME_OVER.
        """
        if self._state != GameState.REPLACING:
            raise RuntimeError("Cannot end round — round is not in progress.")

        self._state = GameState.SCORING
        scores = {}

        for player in self._players:
            score = player.record_round_score(bonus_suit=self._bonus_suit)
            scores[player.get_name()] = score

        if self._current_round >= self._total_rounds:
            self._state = GameState.GAME_OVER
        else:
            self._state = GameState.WAITING

        return scores

    def reset_game(self):
        """Fully reset everything for a brand new game."""
        for player in self._players:
            player.reset()
        self._deck.reset()
        self._current_round = 0
        self._bonus_suit = None
        self._state = GameState.WAITING
        self._replacements_used = {p.get_name(): 0 for p in self._players}

    def __repr__(self):
        return (
            f"Game(round={self._current_round}/{self._total_rounds}, "
            f"state={self._state}, "
            f"bonus_suit={Suit.name(self._bonus_suit) if self._bonus_suit else None})"
        )