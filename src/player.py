from src.hand import Hand


class Player:
    def __init__(self, name):
        if not name or not name.strip():
            raise ValueError("Player name cannot be empty.")
        self._name         = name.strip()
        self._hand         = Hand()
        self._bonus_suit   = None
        self._total_score  = 0
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
        Score = best single suit total.
        +5 bonus if that suit matches the chosen bonus suit.
        Matches Java: maxScore + (5 if maxSuit == bonusSuit).
        """
        scores   = self._hand.suit_scores()
        if not scores:
            self._round_scores.append(0)
            return 0

        best_idx   = max(scores, key=scores.get)
        best_score = scores[best_idx]

        bonus = 0
        if self._bonus_suit is not None:
            from src.card import Suit
            bonus_idx = Suit.index(self._bonus_suit)
            if best_idx == bonus_idx:
                bonus = 5

        round_score = best_score + bonus
        self._round_scores.append(round_score)
        self._total_score += round_score
        return round_score

    def clear_hand(self):
        self._hand.clear()
        self._bonus_suit = None

    def reset(self):
        self._hand.clear()
        self._bonus_suit   = None
        self._total_score  = 0
        self._round_scores = []

    def __str__(self):
        return (
            f"Player: {self._name} | "
            f"Total: {self._total_score} | "
            f"Rounds: {self._round_scores}"
        )

    def __repr__(self):
        return f"Player(name={self._name!r}, total={self._total_score})"