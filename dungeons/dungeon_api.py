from .dungeon import Dungeon
from .dungeon_layout import DungeonLayout
from .dungeon_templates import *
from .dungeon_manager import DungeonManager
from treasure.treasure_api import RawHoardSource
from .dungeon_template_picker import TemplatePicker
from random import Random

class DungeonSource():
    def __init__(self, level, terrain=None, base_type=None, templates=None, main_antagonist=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        if base_type is None:
            base_type = self.random_state.choice(['mine', 'stronghold', 'sewer', 'treasure_vault', 'tomb', 'cave', 'temple'])
        n_rooms=self.random_state.randint(5, 7)
        if base_type == 'treasure vault':
            n_rooms -= 1
        layout = DungeonLayout(n_rooms=n_rooms, random_state=self.random_state)
        templates = TemplatePicker(base_type, supplied_templates=templates, supplied_monster_set=main_antagonist, random_state=self.random_state).pick_set()
        if terrain is None:
            terrain = self.random_state.choice(['forest', 'desert', 'mountains', 'arctic', 'plains', 'hills', 'jungle', 'swamp'])
        with DungeonManager(self.level, layout, terrain=terrain, random_state=self.random_state) as dungeon_manager:
            for template, monster_set in templates:
                template(self.level,
                         dungeon_manager=dungeon_manager,
                         monster_set=monster_set,
                         random_state=self.random_state).alter_dungeon(layout)
        self.dungeon = Dungeon(layout, random_state=self.random_state)

    def get_dungeon(self):
        return self.dungeon.module()



