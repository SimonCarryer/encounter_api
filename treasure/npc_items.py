from .treasure_tables import unique_items, magic_items, item_properties
from random import Random

class NPC_item:
    def __init__(self, level, martial=False, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        if martial:
            self.item_list = unique_items
        else:
            self.item_list = magic_items
        self.level = level
        self.item = self.get_item()
        self.properties = self.get_properties()
        self.name = self.get_name()

    def get_name(self):
        return 'Item name here'

    def rarities(self):
        return ['uncommon', 'rare', 'very rare', 'legendary'][int(round(self.level/10)):max([int(round((self.level)/4)),1])]

    def get_item(self):
        possible_items = sorted([item for item, rarity in self.item_list.items() if rarity in self.rarities()])
        if len(possible_items) == 0:
            item = 'None'
        else:
            item = self.random_state.choice(possible_items)
        return item

    def get_properties(self, n_properties=2):
        tables = self.random_state.sample(item_properties.keys(), n_properties)
        properties = []
        for table in tables:
            properties.append(self.random_state.choice(item_properties[table]))
        return properties