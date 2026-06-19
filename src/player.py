from src.hand import Hand


class Player:
    """
    Represents a human or computer player.
    bonus_suit is chosen by the player each round (not random).
    """

    def __init__(self, name):
        if not name or not name.strip():
            raise ValueError("Player name cannot be empty.")
        self._name        = name.strip()
        self._hand        = Hand()
        self._bonus_suit  = None   # Set each round by the player
        self._total_score = 0
        self._round_scores = []

    def get_name(self):
        return self._name

    def is_computer(self):
        return self._name.lower() == "computer"

    def get_hand(self):
        return self._hand

    def get_bonus_suit(self):
        return self._bonus_suit

    def set_bonus_suit(self, suit):
        """Player nominates this suit as their bonus suit for the round."""
        self._bonus_suit = suit

    def get_total_score(self):
        return self._total_score

    def get_round_scores(self):
        return list(self._round_scores)

    def get_last_round_score(self):
        return self._round_scores[-1] if self._round_scores else 0

    def add_cards(self, cards):
        self._hand.add_cards(cards)

    def replace_card(self, index, new_card):
        self._hand.replace_card(index, new_card)

    def record_round_score(self):
        """
        Score = best single suit value + 5 if it matches bonus suit.
        """
        score = self._hand.get_round_score(bonus_suit=self._bonus_suit)
        self._round_scores.append(score)
        self._total_score += score
        return score

    def clear_hand(self):
        self._hand.clear()
        self._bonus_suit = None

    def reset(self):
        self._hand.clear()
        self._bonus_suit  = None
        self._total_score = 0
        self._round_scores = []

    def __str__(self):
        return (
            f"Player: {self._name} | "
            f"Total: {self._total_score} | "
            f"Rounds: {self._round_scores}"
        )

    def __repr__(self):
        return f"Player(name={self._name!r}, total={self._total_score})"