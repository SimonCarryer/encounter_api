from .dungeon import Dungeon
from .dungeon_layout import DungeonLayout
from .dungeon_templates import some_examples
from .dungeon_manager import DungeonManager
from .special_events import VillainHideout, LostItem, ForbiddingDoor, UnderdarkEntrance
from treasure.treasure_api import RawHoardSource
from random import Random



class DungeonSource():
    def __init__(self, level, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        layout = DungeonLayout(n_rooms=self.random_state.randint(4, 7), random_state=self.random_state)
        templates = self.random_state.choice(some_examples)
        terrain = self.random_state.choice(['forest', 'desert', 'mountains', 'arctic', 'plains', 'hills', 'jungle', 'swamp'])
        with DungeonManager(self.level, layout, terrain=terrain, random_state=self.random_state) as dungeon_manager:
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
        if self.random_state.randint(1, 6) >= 6 and layout.purpose == 'cave':
            special_events.append(UnderdarkEntrance)
        elif self.random_state.randint(1, 10) == 10:
            special_events.append(UnderdarkEntrance)
        if self.random_state.randint(1, 6) >= 5:
            event = self.random_state.choice([VillainHideout, LostItem, ForbiddingDoor])
            special_events.append(event)
        return special_events


