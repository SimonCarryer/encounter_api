from .treasure_tables import item_tables
from .treasure_tables import magic_items
from random import Random

class NPC_item:
    def __init__(self, level, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        self.item = self.get_item()

    def get_item(self):
        rarities = ['common', 'uncommon', 'rare', 'very rare'][int(self.level/10):int(self.level/4)]
        possible_items = sorted([item for item, rarity in magic_items.items() if rarity in rarities])
        if len(possible_items) == 0:
            item = 'None'
        else:
            item = self.random_state.choice(possible_items)
        return item
        