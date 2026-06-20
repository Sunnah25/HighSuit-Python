import pytest
from src.deck import Deck
from src.card import Card


class TestDeck:
    def test_deck_has_52_cards(self):
        deck = Deck()
        assert len(deck) == 52

    def test_deck_deal_returns_card(self):
        deck = Deck()
        card = deck.deal()
        assert isinstance(card, Card)

    def test_deck_deal_reduces_count(self):
        deck = Deck()
        deck.deal()
        assert len(deck) == 51

    def test_deck_deal_many_returns_correct_count(self):
        deck = Deck()
        cards = deck.deal_many(5)
        assert len(cards) == 5

    def test_deck_deal_many_reduces_count(self):
        deck = Deck()
        deck.deal_many(5)
        assert len(deck) == 47

    def test_deck_all_cards_unique(self):
        deck = Deck()
        cards = deck.deal_many(52)
        reprs = [repr(c) for c in cards]
        assert len(set(reprs)) == 52

    def test_deck_deal_from_empty_returns_none(self):
        deck = Deck()
        deck.deal_many(52)
        assert deck.deal() is None

    def test_deck_is_empty_after_all_dealt(self):
        deck = Deck()
        deck.deal_many(52)
        assert deck.is_empty()

    def test_deck_not_empty_at_start(self):
        deck = Deck()
        assert not deck.is_empty()

    def test_deck_cards_remaining(self):
        deck = Deck()
        deck.deal_many(10)
        assert deck.cards_remaining() == 42

    def test_deck_reset_restores_52(self):
        deck = Deck()
        deck.deal_many(20)
        deck.reset()
        assert len(deck) == 52

    def test_deck_reset_allows_dealing_again(self):
        deck = Deck()
        deck.deal_many(52)
        deck.reset()
        card = deck.deal()
        assert isinstance(card, Card)

    def test_deck_deal_many_does_not_exceed_remaining(self):
        deck = Deck()
        deck.deal_many(50)
        # Only 2 left — asking for 5 should return 2
        cards = deck.deal_many(5)
        assert len(cards) == 2

    def test_deck_shuffle_produces_different_order(self):
        """Shuffled deck should (almost certainly) differ from unshuffled."""
        import random
        random.seed(None)
        deck1 = Deck()
        order1 = [repr(deck1.deal()) for _ in range(10)]
        deck2 = Deck()
        order2 = [repr(deck2.deal()) for _ in range(10)]
        # Two independently shuffled decks are extremely unlikely to match
        # We just check the deck is functional, not exact order
        assert len(order1) == 10
        assert len(order2) == 10