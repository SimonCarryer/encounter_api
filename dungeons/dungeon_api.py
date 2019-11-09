from .dungeon import Dungeon
from .dungeon_layout import DungeonLayout
from .dungeon_templates import *
from .dungeon_manager import DungeonManager
from treasure.treasure_api import RawHoardSource
from .dungeon_template_picker import TemplatePicker
from random import Random

class DungeonSource():
    def __init__(self, level, terrain=None, base_type=None, templates=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        layout = DungeonLayout(n_rooms=self.random_state.randint(4, 7), random_state=self.random_state)
        templates = TemplatePicker(base_type, templates, self.random_state).pick_set()
        if terrain is None:
            terrain = self.random_state.choice(['forest', 'desert', 'mountains', 'arctic', 'plains', 'hills', 'jungle', 'swamp'])
        with DungeonManager(self.level, layout, terrain=terrain, random_state=self.random_state) as dungeon_manager:
            for template, monster_set in templates:
                template(self.level,
                         dungeon_manager=dungeon_manager,
                         monster_set=monster_set,
                         random_state=self.random_state).alter_dungeon(layout)
        self.dungeon = Dungeon(layout)

    def get_dungeon(self):
        return self.dungeon.module()



