from src.card import Card, Suit


class Hand:
    """
    Holds a player's 5 cards.
    Scoring follows HighSuit rules:
      - Score = total value of cards in the BEST single suit
      - +5 bonus if that suit matches the chosen bonus suit
    """

    MAX_CARDS = 5

    def __init__(self):
        self._cards = []

    def add_card(self, card):
        if card and len(self._cards) < self.MAX_CARDS:
            self._cards.append(card)

    def add_cards(self, cards):
        for card in cards:
            self.add_card(card)

    def get_card(self, index):
        if 0 <= index < len(self._cards):
            return self._cards[index]
        return None

    def get_all_cards(self):
        return list(self._cards)

    def replace_card(self, index, new_card):
        if 0 <= index < len(self._cards) and new_card:
            self._cards[index] = new_card

    def size(self):
        return len(self._cards)

    def is_full(self):
        return len(self._cards) == self.MAX_CARDS

    def is_empty(self):
        return len(self._cards) == 0

    def clear(self):
        self._cards = []

    def suit_scores(self):
        """
        Returns dict of {suit_index: total_value} for all suits present.
        Card values: 2-9 face value, 10/J/Q/K=10, Ace=11
        """
        scores = {}
        for card in self._cards:
            suit_idx = card.get_suit_index()
            scores[suit_idx] = scores.get(suit_idx, 0) + card.get_value()
        return scores

    def best_suit_index(self):
        """Return the suit index (0-3) with the highest total value."""
        scores = self.suit_scores()
        if not scores:
            return 0
        return max(scores, key=scores.get)

    def best_suit_score(self):
        """Return the highest single-suit total value."""
        scores = self.suit_scores()
        if not scores:
            return 0
        return max(scores.values())

    def get_round_score(self, bonus_suit=None):
        """
        Final round score:
        = best single suit score
        + 5 if that suit matches the player's chosen bonus suit
        """
        scores     = self.suit_scores()
        if not scores:
            return 0
        best_idx   = max(scores, key=scores.get)
        best_score = scores[best_idx]

        bonus = 0
        if bonus_suit is not None:
            bonus_idx = Suit.index(bonus_suit)
            if best_idx == bonus_idx:
                bonus = 5

        return best_score + bonus

    def get_max_possible_score(self):
        """Best score ignoring bonus suit — used by computer player."""
        return self.best_suit_score()

    def __str__(self):
        if not self._cards:
            return "Empty hand"
        return " | ".join(str(c) for c in self._cards)

    def __len__(self):
        return len(self._cards)