from src.hand import Hand


class Player:
    """
    Represents a human player in the HighSuit game.
    Tracks name, current hand, total score, and round history.
    """

    def __init__(self, name):
        if not name or not name.strip():
            raise ValueError("Player name cannot be empty.")
        self._name = name.strip()
        self._hand = Hand()
        self._total_score = 0
        self._round_scores = []

    def get_name(self):
        """Return the player's name."""
        return self._name

    def get_hand(self):
        """Return the player's current hand."""
        return self._hand

    def get_total_score(self):
        """Return the player's cumulative score across all rounds."""
        return self._total_score

    def get_round_scores(self):
        """Return a list of scores from each completed round."""
        return list(self._round_scores)

    def get_last_round_score(self):
        """Return the score from the most recent round, or 0 if no rounds played."""
        if not self._round_scores:
            return 0
        return self._round_scores[-1]

    def add_cards(self, cards):
        """Deal a list of cards into the player's hand."""
        self._hand.add_cards(cards)

    def replace_card(self, index, new_card):
        """Replace a card in hand at the given index with a new card."""
        self._hand.replace_card(index, new_card)

    def record_round_score(self, bonus_suit=None):
        """
        Calculate and store the score for the current round.
        Adds to the running total. Returns the round score.
        """
        round_score = self._hand.get_total_score(bonus_suit)
        self._round_scores.append(round_score)
        self._total_score += round_score
        return round_score

    def clear_hand(self):
        """Clear the player's hand at the end of a round."""
        self._hand.clear()

    def reset(self):
        """Fully reset the player for a new game (clears score history too)."""
        self._hand.clear()
        self._total_score = 0
        self._round_scores = []

    def __str__(self):
        return (
            f"Player: {self._name} | "
            f"Total Score: {self._total_score} | "
            f"Round Scores: {self._round_scores}"
        )

    def __repr__(self):
        return f"Player(name={self._name!r}, total_score={self._total_score})"