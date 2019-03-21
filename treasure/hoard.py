from random import Random
import bisect
from .treasure_tables import treasure_tables, item_tables

class Hoard:
    def __init__(self, level, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        self.objects, self.items, self.coins = self.roll_on_treasure_table()

    def find_appropriate_treasure_table(self):
        levels = sorted([i for i in treasure_tables.keys()])
        level = levels[bisect.bisect_left(levels, self.level)]
        return treasure_tables[level]

    def get_objects(self, die_n, die_sides, object_type, value):
        if die_n == '':
            return "No art objects or gems."
        roll = sum([self.random_state.randint(1, int(die_sides)) for _ in range(int(die_n))])
        total = int(roll)*int(value)
        return "%d %ss of value %dgp each (total %dgp)" % (int(roll), object_type, int(value), total)

    def get_items(self, die_sides, table_name):
        if die_sides == '':
            items = []
        else:
            roll = self.random_state.randint(1, int(die_sides))
            items = [self.roll_on_item_tables(table_name) for _ in range(roll)]
        return items

    def get_coins(self, coin_type, die_n, die_sides, multiplier):
        roll = sum([self.random_state.randint(1, int(die_sides)) for _ in range(int(die_n))])
        total = roll * int(multiplier)
        return "%s %s" % ("{:,}".format(total), coin_type)


    def roll_on_treasure_table(self):
        table = self.find_appropriate_treasure_table()
        chances = [int(i['chance']) for i in table['objects']]
        roll = self.random_state.randint(1, 100)
        index = bisect.bisect_left(chances, roll)
        row = table['objects'][index]
        objects = self.get_objects(row['object_die_n'], row['object_die_sides'], row['object_type'], row['object_value'])
        items = self.get_items(row['item_die_sides'], row['item_table_name'])
        coins = []
        for coin_type in table['coins']:
            coins.append(self.get_coins(coin_type['name'], coin_type['die_n'], coin_type['die_sides'], coin_type['multiplier']))
        return objects, items, coins

    def roll_on_item_tables(self, table_name):
        chances = sorted(item_tables[table_name]['chance'])
        items = item_tables[table_name]['items']
        roll = self.random_state.randint(1, 100)
        index = bisect.bisect_left(chances, roll)
        return items[index]
