import pytest
from src.hand import Hand
from src.card import Card, Suit, Rank


def make_hand(*suit_rank_pairs):
    """Helper — build a Hand from (suit, rank) tuples."""
    hand = Hand()
    for suit, rank in suit_rank_pairs:
        hand.add_card(Card(suit, rank))
    return hand


class TestHand:
    def test_empty_hand_size_is_zero(self):
        assert Hand().size() == 0

    def test_add_card_increases_size(self):
        hand = Hand()
        hand.add_card(Card(Suit.HEARTS, Rank.ACE))
        assert hand.size() == 1

    def test_hand_max_five_cards(self):
        hand = Hand()
        for rank in Rank.ALL[:6]:
            hand.add_card(Card(Suit.CLUBS, rank))
        assert hand.size() == 5

    def test_get_card_returns_correct_card(self):
        hand = make_hand((Suit.HEARTS, Rank.ACE))
        assert hand.get_card(0).get_rank() == Rank.ACE

    def test_get_card_out_of_range_returns_none(self):
        hand = make_hand((Suit.HEARTS, Rank.ACE))
        assert hand.get_card(5) is None
        assert hand.get_card(-1) is None

    def test_replace_card(self):
        hand = make_hand(
            (Suit.HEARTS,   Rank.TWO),
            (Suit.DIAMONDS, Rank.THREE),
        )
        new_card = Card(Suit.SPADES, Rank.ACE)
        hand.replace_card(0, new_card)
        assert hand.get_card(0) == new_card

    def test_replace_card_invalid_index(self):
        hand = make_hand((Suit.HEARTS, Rank.ACE))
        hand.replace_card(9, Card(Suit.CLUBS, Rank.TWO))
        # Should not crash — invalid index silently ignored
        assert hand.size() == 1

    def test_clear_empties_hand(self):
        hand = make_hand(
            (Suit.HEARTS, Rank.ACE),
            (Suit.CLUBS,  Rank.KING),
        )
        hand.clear()
        assert hand.size() == 0
        assert hand.is_empty()

    def test_is_full(self):
        hand = Hand()
        for rank in Rank.ALL[:5]:
            hand.add_card(Card(Suit.CLUBS, rank))
        assert hand.is_full()

    def test_not_full_with_four_cards(self):
        hand = Hand()
        for rank in Rank.ALL[:4]:
            hand.add_card(Card(Suit.CLUBS, rank))
        assert not hand.is_full()

    def test_suit_scores_single_suit(self):
        """All clubs: 2+3+4+5+6 = 20"""
        hand = make_hand(
            (Suit.CLUBS, Rank.TWO),
            (Suit.CLUBS, Rank.THREE),
            (Suit.CLUBS, Rank.FOUR),
            (Suit.CLUBS, Rank.FIVE),
            (Suit.CLUBS, Rank.SIX),
        )
        scores = hand.suit_scores()
        assert scores[Suit.index(Suit.CLUBS)] == 20

    def test_suit_scores_mixed_suits(self):
        hand = make_hand(
            (Suit.HEARTS,   Rank.ACE),    # 11
            (Suit.HEARTS,   Rank.KING),   # 10
            (Suit.SPADES,   Rank.TWO),    # 2
            (Suit.DIAMONDS, Rank.THREE),  # 3
            (Suit.CLUBS,    Rank.FOUR),   # 4
        )
        scores = hand.suit_scores()
        assert scores[Suit.index(Suit.HEARTS)] == 21
        assert scores[Suit.index(Suit.SPADES)] == 2

    def test_best_suit_index_picks_highest(self):
        hand = make_hand(
            (Suit.HEARTS, Rank.ACE),    # 11
            (Suit.HEARTS, Rank.KING),   # 10
            (Suit.CLUBS,  Rank.TWO),    # 2
            (Suit.CLUBS,  Rank.THREE),  # 3
            (Suit.CLUBS,  Rank.FOUR),   # 4
        )
        # Hearts = 21, Clubs = 9 — Hearts should win
        assert hand.best_suit_index() == Suit.index(Suit.HEARTS)

    def test_best_suit_score(self):
        hand = make_hand(
            (Suit.HEARTS, Rank.ACE),   # 11
            (Suit.HEARTS, Rank.KING),  # 10
            (Suit.CLUBS,  Rank.TWO),   # 2
            (Suit.CLUBS,  Rank.THREE), # 3
            (Suit.CLUBS,  Rank.FOUR),  # 4
        )
        assert hand.best_suit_score() == 21

    def test_round_score_no_bonus(self):
        """Best suit = Hearts (21), bonus suit = Clubs — no bonus."""
        hand = make_hand(
            (Suit.HEARTS, Rank.ACE),   # 11
            (Suit.HEARTS, Rank.KING),  # 10
            (Suit.CLUBS,  Rank.TWO),   # 2
            (Suit.CLUBS,  Rank.THREE), # 3
            (Suit.CLUBS,  Rank.FOUR),  # 4
        )
        score = hand.get_round_score(bonus_suit=Suit.CLUBS)
        assert score == 21   # Best suit Hearts, bonus was Clubs — no +5

    def test_round_score_with_bonus(self):
        """Best suit = Hearts (21), bonus suit = Hearts — +5 bonus."""
        hand = make_hand(
            (Suit.HEARTS, Rank.ACE),   # 11
            (Suit.HEARTS, Rank.KING),  # 10
            (Suit.CLUBS,  Rank.TWO),   # 2
            (Suit.CLUBS,  Rank.THREE), # 3
            (Suit.CLUBS,  Rank.FOUR),  # 4
        )
        score = hand.get_round_score(bonus_suit=Suit.HEARTS)
        assert score == 26   # 21 + 5 bonus

    def test_round_score_no_bonus_suit(self):
        """No bonus suit passed — just best suit score."""
        hand = make_hand(
            (Suit.SPADES, Rank.ACE),   # 11
            (Suit.SPADES, Rank.KING),  # 10
            (Suit.CLUBS,  Rank.TWO),   # 2
            (Suit.CLUBS,  Rank.THREE), # 3
            (Suit.CLUBS,  Rank.FOUR),  # 4
        )
        score = hand.get_round_score(bonus_suit=None)
        assert score == 21

    def test_all_same_suit_score(self):
        """5 aces of spades = 55, + 5 bonus = 60."""
        hand = make_hand(
            (Suit.SPADES, Rank.ACE),
            (Suit.SPADES, Rank.ACE),
            (Suit.SPADES, Rank.ACE),
            (Suit.SPADES, Rank.ACE),
            (Suit.SPADES, Rank.ACE),
        )
        assert hand.get_round_score(bonus_suit=Suit.SPADES) == 60

    def test_picture_cards_score_10_each(self):
        """J + Q + K of hearts = 30."""
        hand = make_hand(
            (Suit.HEARTS, Rank.JACK),
            (Suit.HEARTS, Rank.QUEEN),
            (Suit.HEARTS, Rank.KING),
            (Suit.CLUBS,  Rank.TWO),
            (Suit.CLUBS,  Rank.THREE),
        )
        scores = hand.suit_scores()
        assert scores[Suit.index(Suit.HEARTS)] == 30