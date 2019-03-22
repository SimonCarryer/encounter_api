from .treasure_tables import individual_tables
import bisect
from collections import defaultdict

coin_values = {
    'CP': 0.01,
    'SP': 0.1,
    'GP': 1.0,
    'EP': 2.0,
    'PP': 5.0
}

class Individual:
    def __init__(self, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.coins = defaultdict(int)
        self.objects = None

    def find_appropriate_table(self, level):
        levels = sorted([i for i in individual_tables.keys()])
        level = levels[bisect.bisect_left(levels, level)]
        return individual_tables[level]

    def get_coins(self, die_n, die_sides, multiplier):
        roll = sum([self.random_state.randint(1, int(die_sides)) for _ in range(int(die_n))])
        total = roll * int(multiplier)
        return total

    def generate_treasure(self, list_of_monster_levels):
        for monster_level in list_of_monster_levels:
            self.roll_on_table(monster_level)
        self.coins_to_objects()
        

    def coins_to_objects(self):
        value = 0
        coin_types = []
        while sum(self.coins.values()) >= 300 or len(coin_types) > 3:
            coin_types = sorted([coin_type for coin_type, value in self.coins.items() if value > 0])
            coin_type = self.random_state.choice(coin_types)
            n_coins = self.coins[coin_type]
            self.coins[coin_type] = 0
            value += (n_coins * coin_values[coin_type])
        value = round(value, -1)
        if value > 0:
            self.objects = 'Gemstones and jewelry worth %dGP.' % value


    def roll_on_table(self, level):
        table = self.find_appropriate_table(level)
        chances = sorted(list(table.keys()))
        roll = self.random_state.randint(1, 100)
        index = bisect.bisect_left(chances, roll)
        rows = table[chances[index]]
        for coin_type in rows:
            self.coins[coin_type['name']] += self.get_coins(coin_type['die_n'], coin_type['die_sides'], coin_type['multiplier'])
        return self.coins

