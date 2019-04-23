from .dungeon import Dungeon
from .dungeon_layout import DungeonLayout
from .dungeon_templates import some_examples
from treasure.treasure_manager import TreasureManager
from treasure.treasure_api import RawHoardSource
from random import Random



class DungeonSource():
    def __init__(self, level, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        layout = DungeonLayout(n_rooms=self.random_state.randint(5, 8))
        templates = self.random_state.choice(some_examples)
        treasure_manager = TreasureManager(RawHoardSource(self.level, random_state=self.random_state).get_treasure(), random_state=self.random_state)
        for template in templates:
            template(self.level, treasure_manager=treasure_manager, random_state=self.random_state).alter_dungeon(layout)
        self.dungeon = Dungeon(layout)

    def get_dungeon(self):
        return self.dungeon.module()

