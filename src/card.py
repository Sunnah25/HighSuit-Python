class Suit:
    CLUBS    = ("Clubs",    0)
    DIAMONDS = ("Diamonds", 1)
    HEARTS   = ("Hearts",   2)
    SPADES   = ("Spades",   3)

    ALL = [CLUBS, DIAMONDS, HEARTS, SPADES]

    @staticmethod
    def name(suit):
        return suit[0]

    @staticmethod
    def index(suit):
        return suit[1]

    @staticmethod
    def from_index(i):
        return Suit.ALL[i]


class Rank:
    TWO   = ("2",  0)
    THREE = ("3",  1)
    FOUR  = ("4",  2)
    FIVE  = ("5",  3)
    SIX   = ("6",  4)
    SEVEN = ("7",  5)
    EIGHT = ("8",  6)
    NINE  = ("9",  7)
    TEN   = ("10", 8)
    JACK  = ("J",  9)
    QUEEN = ("Q",  10)
    KING  = ("K",  11)
    ACE   = ("A",  12)

    ALL = [TWO, THREE, FOUR, FIVE, SIX, SEVEN,
           EIGHT, NINE, TEN, JACK, QUEEN, KING, ACE]

    @staticmethod
    def name(rank):
        return rank[0]

    @staticmethod
    def index(rank):
        return rank[1]

    @staticmethod
    def card_value(rank):
        """
        Score value as per HighSuit rules:
        2-9 → face value, 10/J/Q/K → 10, Ace → 11
        """
        i = rank[1]
        if i <= 7:       # 2–9
            return i + 2
        elif i <= 11:    # 10, J, Q, K
            return 10
        else:            # Ace
            return 11


class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def get_value(self):
        return Rank.card_value(self.rank)

    def get_suit_index(self):
        return Suit.index(self.suit)

    def __str__(self):
        rank_names = {
            "2": "Two",   "3": "Three", "4": "Four",
            "5": "Five",  "6": "Six",   "7": "Seven",
            "8": "Eight", "9": "Nine",  "10": "Ten",
            "J": "Jack",  "Q": "Queen", "K": "King", "A": "Ace"
        }
        rank_label = rank_names.get(Rank.name(self.rank), Rank.name(self.rank))
        return f"{rank_label} of {Suit.name(self.suit)}"

    def __repr__(self):
        return f"Card({Rank.name(self.rank)}{Suit.name(self.suit)[0]})"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return False
        return self.suit == other.suit and self.rank == other.rank