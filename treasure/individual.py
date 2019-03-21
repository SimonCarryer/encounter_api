from .treasure_tables import individual_tables
import bisect

class Individual:
    def __init__(self, level, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        self.coins = self.roll_on_table()

    def find_appropriate_table(self):
        levels = sorted([i for i in individual_tables.keys()])
        level = levels[bisect.bisect_left(levels, self.level)]
        return individual_tables[level]

    def get_coins(self, coin_type, die_n, die_sides, multiplier):
        roll = sum([self.random_state.randint(1, int(die_sides)) for _ in range(int(die_n))])
        total = roll * int(multiplier)
        return "%s %s" % ("{:,}".format(total), coin_type)

    def roll_on_table(self):
        table = self.find_appropriate_table()
        chances = sorted(list(table.keys()))
        roll = self.random_state.randint(1, 100)
        index = bisect.bisect_left(chances, roll)
        rows = table[chances[index]]
        coins = []
        for coin_type in rows:
            coins.append(self.get_coins(coin_type['name'], coin_type['die_n'], coin_type['die_sides'], coin_type['multiplier']))
        return coins

