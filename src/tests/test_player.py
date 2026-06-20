import pytest
from src.player import Player
from src.card import Card, Suit, Rank
from src.hand import Hand


def make_player_with_hand(name, suit_rank_pairs):
    """Helper — create a player and give them specific cards."""
    player = Player(name)
    for suit, rank in suit_rank_pairs:
        player.get_hand().add_card(Card(suit, rank))
    return player


class TestPlayer:
    def test_player_name(self):
        p = Player("Sunnah")
        assert p.get_name() == "Sunnah"

    def test_player_name_stripped(self):
        p = Player("  Sunnah  ")
        assert p.get_name() == "Sunnah"

    def test_empty_name_raises(self):
        with pytest.raises(ValueError):
            Player("")

    def test_blank_name_raises(self):
        with pytest.raises(ValueError):
            Player("   ")

    def test_initial_score_zero(self):
        assert Player("Sunnah").get_total_score() == 0

    def test_initial_round_scores_empty(self):
        assert Player("Sunnah").get_round_scores() == []

    def test_is_computer_false(self):
        assert not Player("Sunnah").is_computer()

    def test_is_computer_true(self):
        assert Player("Computer").is_computer()

    def test_is_computer_case_insensitive(self):
        assert Player("computer").is_computer()
        assert Player("COMPUTER").is_computer()

    def test_set_and_get_bonus_suit(self):
        p = Player("Sunnah")
        p.set_bonus_suit(Suit.HEARTS)
        assert p.get_bonus_suit() == Suit.HEARTS

    def test_record_round_score_no_bonus(self):
        """Hearts = 21, bonus = Clubs → score = 21."""
        p = make_player_with_hand("Sunnah", [
            (Suit.HEARTS, Rank.ACE),    # 11
            (Suit.HEARTS, Rank.KING),   # 10
            (Suit.CLUBS,  Rank.TWO),    # 2
            (Suit.CLUBS,  Rank.THREE),  # 3
            (Suit.CLUBS,  Rank.FOUR),   # 4
        ])
        p.set_bonus_suit(Suit.CLUBS)
        score = p.record_round_score()
        assert score == 21
        assert p.get_total_score() == 21
        assert p.get_round_scores() == [21]

    def test_record_round_score_with_bonus(self):
        """Hearts = 21, bonus = Hearts → score = 26."""
        p = make_player_with_hand("Sunnah", [
            (Suit.HEARTS, Rank.ACE),    # 11
            (Suit.HEARTS, Rank.KING),   # 10
            (Suit.CLUBS,  Rank.TWO),    # 2
            (Suit.CLUBS,  Rank.THREE),  # 3
            (Suit.CLUBS,  Rank.FOUR),   # 4
        ])
        p.set_bonus_suit(Suit.HEARTS)
        score = p.record_round_score()
        assert score == 26
        assert p.get_total_score() == 26

    def test_multiple_rounds_accumulate(self):
        p = make_player_with_hand("Sunnah", [
            (Suit.HEARTS, Rank.ACE),
            (Suit.HEARTS, Rank.KING),
            (Suit.CLUBS,  Rank.TWO),
            (Suit.CLUBS,  Rank.THREE),
            (Suit.CLUBS,  Rank.FOUR),
        ])
        p.set_bonus_suit(Suit.HEARTS)
        p.record_round_score()   # 26

        p.clear_hand()
        p.get_hand().add_card(Card(Suit.SPADES, Rank.ACE))
        p.get_hand().add_card(Card(Suit.SPADES, Rank.KING))
        p.get_hand().add_card(Card(Suit.CLUBS,  Rank.TWO))
        p.get_hand().add_card(Card(Suit.CLUBS,  Rank.THREE))
        p.get_hand().add_card(Card(Suit.CLUBS,  Rank.FOUR))
        p.set_bonus_suit(Suit.SPADES)
        p.record_round_score()   # 26

        assert p.get_total_score() == 52
        assert len(p.get_round_scores()) == 2

    def test_get_last_round_score(self):
        p = make_player_with_hand("Sunnah", [
            (Suit.HEARTS, Rank.ACE),
            (Suit.HEARTS, Rank.KING),
            (Suit.CLUBS,  Rank.TWO),
            (Suit.CLUBS,  Rank.THREE),
            (Suit.CLUBS,  Rank.FOUR),
        ])
        p.set_bonus_suit(Suit.HEARTS)
        p.record_round_score()
        assert p.get_last_round_score() == 26

    def test_get_last_round_score_no_rounds(self):
        assert Player("Sunnah").get_last_round_score() == 0

    def test_clear_hand_clears_bonus_suit(self):
        p = Player("Sunnah")
        p.set_bonus_suit(Suit.HEARTS)
        p.clear_hand()
        assert p.get_bonus_suit() is None

    def test_reset_clears_everything(self):
        p = make_player_with_hand("Sunnah", [
            (Suit.HEARTS, Rank.ACE),
            (Suit.HEARTS, Rank.KING),
            (Suit.CLUBS,  Rank.TWO),
            (Suit.CLUBS,  Rank.THREE),
            (Suit.CLUBS,  Rank.FOUR),
        ])
        p.set_bonus_suit(Suit.HEARTS)
        p.record_round_score()
        p.reset()
        assert p.get_total_score()   == 0
        assert p.get_round_scores()  == []
        assert p.get_bonus_suit()    is None
        assert p.get_hand().is_empty()

    def test_add_cards(self):
        p = Player("Sunnah")
        cards = [Card(Suit.HEARTS, Rank.ACE), Card(Suit.CLUBS, Rank.KING)]
        p.add_cards(cards)
        assert p.get_hand().size() == 2

    def test_replace_card(self):
        p = make_player_with_hand("Sunnah", [
            (Suit.HEARTS, Rank.TWO),
            (Suit.CLUBS,  Rank.THREE),
        ])
        new_card = Card(Suit.SPADES, Rank.ACE)
        p.replace_card(0, new_card)
        assert p.get_hand().get_card(0) == new_card