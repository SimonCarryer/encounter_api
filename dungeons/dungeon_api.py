from .dungeon import Dungeon
from .dungeon_layout import DungeonLayout
from .dungeon_templates import some_examples
from .dungeon_manager import DungeonManager
from .special_events import VillainHideout, LostItem, Prison
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
        terrain = self.random_state.choice(['forest', 'desert', 'mountains', 'arctic', 'plains', 'hills', 'jungle', 'swamp'])
        with DungeonManager(self.level, layout, terrain=terrain) as dungeon_manager:
            for template in templates:
                template(self.level,
                         dungeon_manager=dungeon_manager,
                         random_state=self.random_state).alter_dungeon(layout)
            for special_event in self.special_events(layout):
                special_event(self.level, dungeon_manager, random_state=self.random_state).alter_dungeon(layout)
        self.dungeon = Dungeon(layout)

    def get_dungeon(self):
        return self.dungeon.module()

    def special_events(self, layout):
        special_events = []
        if self.random_state.randint(1, 6) >= 5:
            event = self.random_state.choice([VillainHideout, LostItem, Prison])
            special_events.append(event)
        return special_events


