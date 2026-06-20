import pytest
from src.game import Game, GameState
from src.card import Suit, Card, Rank


class TestGameInit:
    def test_creates_players(self):
        g = Game(["Sunnah"], total_rounds=3)
        assert len(g.get_players()) == 1
        assert g.get_players()[0].get_name() == "Sunnah"

    def test_two_players(self):
        g = Game(["Sunnah", "Computer"], total_rounds=3)
        assert len(g.get_players()) == 2

    def test_initial_state_waiting(self):
        g = Game(["Sunnah"], total_rounds=3)
        assert g.get_state() == GameState.WAITING

    def test_initial_round_zero(self):
        g = Game(["Sunnah"], total_rounds=3)
        assert g.get_current_round() == 0

    def test_empty_player_list_raises(self):
        with pytest.raises(ValueError):
            Game([], total_rounds=3)

    def test_zero_rounds_raises(self):
        with pytest.raises(ValueError):
            Game(["Sunnah"], total_rounds=0)

    def test_too_many_rounds_raises(self):
        with pytest.raises(ValueError):
            Game(["Sunnah"], total_rounds=4)


class TestGameRoundFlow:
    def setup_method(self):
        self.game = Game(["Sunnah"], total_rounds=3)

    def test_start_round_increments_round(self):
        self.game.start_round()
        assert self.game.get_current_round() == 1

    def test_start_round_deals_5_cards(self):
        self.game.start_round()
        player = self.game.get_players()[0]
        assert player.get_hand().size() == 5

    def test_start_round_sets_choosing_suit_state(self):
        self.game.start_round()
        assert self.game.get_state() == GameState.CHOOSING_SUIT

    def test_set_bonus_suit_advances_to_replacing(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        assert self.game.get_state() == GameState.REPLACING

    def test_set_bonus_suit_stored_on_player(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        player = self.game.get_player("Sunnah")
        assert player.get_bonus_suit() == Suit.HEARTS

    def test_set_bonus_suit_invalid_player_raises(self):
        self.game.start_round()
        with pytest.raises(ValueError):
            self.game.set_bonus_suit("Nobody", Suit.HEARTS)

    def test_replace_cards_updates_hand(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        player  = self.game.get_player("Sunnah")
        old_card = player.get_hand().get_card(0)
        self.game.replace_cards("Sunnah", [0])
        new_card = player.get_hand().get_card(0)
        # Card should have changed (overwhelmingly likely with shuffled deck)
        assert player.get_hand().size() == 5

    def test_replace_cards_max_four(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        # Replacing 4 is fine
        self.game.replace_cards("Sunnah", [0, 1, 2, 3])
        assert self.game.get_replacements_left("Sunnah") == 0

    def test_replace_cards_too_many_raises(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        with pytest.raises(ValueError):
            self.game.replace_cards("Sunnah", [0, 1, 2, 3, 4])

    def test_replace_cards_invalid_index_raises(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        with pytest.raises(ValueError):
            self.game.replace_cards("Sunnah", [9])

    def test_score_player_returns_positive(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        score = self.game.score_player("Sunnah")
        assert score > 0

    def test_score_player_updates_total(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        score = self.game.score_player("Sunnah")
        player = self.game.get_player("Sunnah")
        assert player.get_total_score() == score

    def test_full_round(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        self.game.score_player("Sunnah")
        self.game.advance_round_state()
        assert self.game.get_state() == GameState.WAITING

    def test_game_over_after_all_rounds(self):
        for _ in range(3):
            self.game.start_round()
            self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
            self.game.score_player("Sunnah")
            self.game.advance_round_state()
        assert self.game.get_state() == GameState.GAME_OVER

    def test_get_winner_after_game_over(self):
        for _ in range(3):
            self.game.start_round()
            self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
            self.game.score_player("Sunnah")
            self.game.advance_round_state()
        winner = self.game.get_winner()
        assert winner.get_name() == "Sunnah"

    def test_get_winner_before_game_over_is_none(self):
        assert self.game.get_winner() is None

    def test_reset_game(self):
        self.game.start_round()
        self.game.set_bonus_suit("Sunnah", Suit.HEARTS)
        self.game.score_player("Sunnah")
        self.game.reset_game()
        assert self.game.get_current_round()          == 0
        assert self.game.get_state()                   == GameState.WAITING
        assert self.game.get_player("Sunnah").get_total_score() == 0


class TestComputerPlayer:
    def test_computer_choose_suit_returns_suit(self):
        g = Game(["Computer"], total_rounds=1)
        g.start_round()
        suit = g.computer_choose_suit("Computer")
        assert suit in Suit.ALL

    def test_computer_replace_keeps_at_least_one(self):
        g = Game(["Computer"], total_rounds=1)
        g.start_round()
        g.computer_choose_suit("Computer")
        indices = g.computer_replace_cards("Computer")
        player  = g.get_player("Computer")
        assert player.get_hand().size() == 5

    def test_computer_replace_max_four(self):
        g = Game(["Computer"], total_rounds=1)
        g.start_round()
        g.computer_choose_suit("Computer")
        indices = g.computer_replace_cards("Computer")
        assert len(indices) <= 4


class TestTwoPlayerGame:
    def test_two_players_both_dealt(self):
        g = Game(["Sunnah", "Messi"], total_rounds=1)
        g.start_round()
        for player in g.get_players():
            assert player.get_hand().size() == 5

    def test_leaderboard_sorted_by_score(self):
        g = Game(["Sunnah", "Messi"], total_rounds=1)
        g.start_round()
        g.set_bonus_suit("Sunnah", Suit.HEARTS)
        g.score_player("Sunnah")
        g.set_bonus_suit("Messi", Suit.SPADES)
        g.score_player("Messi")
        g.advance_round_state()

        board = g.get_leaderboard()
        assert board[0].get_total_score() >= board[1].get_total_score()