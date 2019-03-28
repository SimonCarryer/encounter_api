from .dungeon_history import DungeonHistory
from .dungeon_furnisher import DungeonFurnisher
from .dungeon_layout import DungeonLayout
from random import Random

class Dungeon:
    def __init__(self,
                 purpose,
                 events,
                 encounter_level,
                 random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        layout = DungeonLayout(6, connectivity_threshold=1.2, random_state=self.random_state)
        DungeonFurnisher(purpose, random_state=self.random_state).furnish(layout)
        DungeonHistory(events, encounter_level, random_state=self.random_state).alter_dungeon(layout)
        self.layout = layout
