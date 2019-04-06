from .dungeon_history import DungeonHistory
from .dungeon_furnisher import DungeonFurnisher
from .dungeon_layout import DungeonLayout
from random import Random

example_specifications = {
    'inhabitants': {
        'original_inhabitants': 'haunted',
        'new_explorers': 'goblins',
        'level': 3
        },
    'purpose': 'stronghold'
}

class Dungeon:
    def __init__(self,
                 specifications,
                 random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        layout = DungeonLayout(6, connectivity_threshold=1.2, random_state=self.random_state)
        DungeonFurnisher(specifications['purpose'], random_state=self.random_state).furnish(layout)
        DungeonHistory(specifications['inhabitants'], random_state=self.random_state).alter_dungeon(layout)
        self.layout = layout


