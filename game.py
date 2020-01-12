import random
from enum import Enum

class Category(Enum):
    ones            = 1
    twos            = 2
    threes          = 3
    fours           = 4
    fives           = 5
    sixes           = 6

    three_of_a_kind = 7
    four_of_a_kind  = 8
    full_house      = 9
    small_straight  = 10
    large_straght   = 11
    yahtzee         = 12
    chance          = 13


class YahtzeeGame: # just single player for now
    def __init__(self):
        self.state = "started"
        self.current_hand = [random.randint(1, 6) for _ in range(5)]
        self.remaining_rerolls = 2
        self.filled_categories = set()
        self.score_calc = {
            Category.ones: lambda x: sum(filter(lambda i: i == 1, x)),
            Category.twos: lambda x: sum(filter(lambda i: i == 2, x)),
            Category.threes: lambda x: sum(filter(lambda i: i == 3, x)),
            Category.fours: lambda x: sum(filter(lambda i: i == 4, x)),
            Category.fives: lambda x: sum(filter(lambda i: i == 5, x)),
            Category.sixes: lambda x: sum(filter(lambda i: i == 6, x)),

            Category.three_of_a_kind: lambda x: sum(x) if any(x.count(e) >= 3 for e in x) else 0,
            Category.four_of_a_kind: lambda x: sum(x) if any(x.count(e) >= 4 for e in x) else 0,
            Category.full_house: lambda x: 25 if len(set(x)) == 2 and x.count(x[0]) in [2,3] else 0,
            Category.small_straight: lambda x: 30 if any(s.issubset(x) for s in [{1,2,3,4}, {2,3,4,5}, {3,4,5,6}]) else 0,
            Category.large_straght: lambda x: 40 if set(x) in [{1,2,3,4,5}, {2,3,4,5,6}] else 0,
            Category.yahtzee: lambda x: 50 if len(set(x)) == 1 else 0,
            Category.chance: lambda x: sum(x)
        }
        self.scoreboard = {cat.name:0 for cat in Category}
        self.submitted_hands = {cat.name:None for cat in Category}

    def get_unfilled_categories(self):
        return set(x.name for x in Category) - self.filled_categories

    # input: category as a string, e.g. "ones"
    def get_possible_score(self, category):
        return self.score_calc[Category[category]](self.current_hand)

    def get_current_hand(self):
        return self.current_hand

    # input: list of indices to hold; reroll all that are not held.
    def reroll(self, held):
        if self.remaining_rerolls <= 0:
            raise ValueError("You cannot reroll again!")
        if len(held) == 0:
            raise ValueError("No dice selected! Cannot reroll.")

        need_reroll = {0,1,2,3,4} - set(held)
        for i in need_reroll:
            self.current_hand[i] = random.randint(1,6)
        self.remaining_rerolls -= 1

    # input: category as a string, e.g. "ones"
    def submit_hand(self, category):
        if category in self.filled_categories:
            raise ValueError("This category has already been filled in!")

        self.scoreboard[category] = self.get_possible_score(category)
        self.submitted_hands[category] = self.current_hand.copy()
        self.filled_categories.add(category)

        self.current_hand = [random.randint(1, 6) for _ in range(5)]
        self.remaining_rerolls = 2

    def get_current_score(self):
        total_score = sum(self.scoreboard.values())

        # upper score bonus
        upper_score = sum(self.scoreboard[upper_cat.name] for upper_cat in [Category.ones, Category.twos, Category.threes, Category.fours, Category.fives, Category.sixes])
        if upper_score >= 63:
            total_score += 35

        # extra yahtzee bonuses
        if self.scoreboard[Category.yahtzee.name] == 50:
            for cat in self.filled_categories - {Category.yahtzee.name}:
                if len(set(self.submitted_hands[cat])) == 1:
                    total_score += 50

        return total_score