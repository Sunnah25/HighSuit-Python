import pytest
from src.card import Card, Suit, Rank


class TestSuit:
    def test_all_has_four_suits(self):
        assert len(Suit.ALL) == 4

    def test_suit_names(self):
        names = [Suit.name(s) for s in Suit.ALL]
        assert "Clubs"    in names
        assert "Diamonds" in names
        assert "Hearts"   in names
        assert "Spades"   in names

    def test_suit_indices_unique(self):
        indices = [Suit.index(s) for s in Suit.ALL]
        assert len(set(indices)) == 4

    def test_suit_indices_are_0_to_3(self):
        indices = sorted(Suit.index(s) for s in Suit.ALL)
        assert indices == [0, 1, 2, 3]

    def test_from_index_roundtrip(self):
        for suit in Suit.ALL:
            assert Suit.from_index(Suit.index(suit)) == suit


class TestRank:
    def test_all_has_13_ranks(self):
        assert len(Rank.ALL) == 13

    def test_two_value(self):
        assert Rank.card_value(Rank.TWO) == 2

    def test_nine_value(self):
        assert Rank.card_value(Rank.NINE) == 9

    def test_ten_value(self):
        assert Rank.card_value(Rank.TEN) == 10

    def test_jack_value(self):
        assert Rank.card_value(Rank.JACK) == 10

    def test_queen_value(self):
        assert Rank.card_value(Rank.QUEEN) == 10

    def test_king_value(self):
        assert Rank.card_value(Rank.KING) == 10

    def test_ace_value(self):
        assert Rank.card_value(Rank.ACE) == 11

    def test_picture_cards_all_score_10(self):
        for rank in [Rank.JACK, Rank.QUEEN, Rank.KING]:
            assert Rank.card_value(rank) == 10

    def test_number_cards_score_face_value(self):
        expected = {
            Rank.TWO: 2, Rank.THREE: 3, Rank.FOUR: 4,
            Rank.FIVE: 5, Rank.SIX: 6, Rank.SEVEN: 7,
            Rank.EIGHT: 8, Rank.NINE: 9,
        }
        for rank, value in expected.items():
            assert Rank.card_value(rank) == value


class TestCard:
    def test_card_stores_suit_and_rank(self):
        card = Card(Suit.SPADES, Rank.ACE)
        assert card.get_suit() == Suit.SPADES
        assert card.get_rank() == Rank.ACE

    def test_card_value_ace(self):
        card = Card(Suit.HEARTS, Rank.ACE)
        assert card.get_value() == 11

    def test_card_value_king(self):
        card = Card(Suit.CLUBS, Rank.KING)
        assert card.get_value() == 10

    def test_card_value_two(self):
        card = Card(Suit.DIAMONDS, Rank.TWO)
        assert card.get_value() == 2

    def test_card_suit_index(self):
        card = Card(Suit.HEARTS, Rank.TEN)
        assert card.get_suit_index() == Suit.index(Suit.HEARTS)

    def test_card_str(self):
        card = Card(Suit.SPADES, Rank.ACE)
        assert "Ace" in str(card)
        assert "Spades" in str(card)

    def test_card_repr(self):
        card = Card(Suit.CLUBS, Rank.KING)
        assert "K" in repr(card)
        assert "C" in repr(card)

    def test_card_equality(self):
        c1 = Card(Suit.HEARTS, Rank.QUEEN)
        c2 = Card(Suit.HEARTS, Rank.QUEEN)
        assert c1 == c2

    def test_card_inequality_different_suit(self):
        c1 = Card(Suit.HEARTS, Rank.ACE)
        c2 = Card(Suit.SPADES, Rank.ACE)
        assert c1 != c2

    def test_card_inequality_different_rank(self):
        c1 = Card(Suit.HEARTS, Rank.ACE)
        c2 = Card(Suit.HEARTS, Rank.KING)
        assert c1 != c2

    def test_card_not_equal_to_non_card(self):
        card = Card(Suit.HEARTS, Rank.ACE)
        assert card != "Ace of Hearts"
        assert card != 11
        assert card != None