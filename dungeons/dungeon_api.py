from .dungeon import Dungeon
from .dungeon_layout import DungeonLayout
from .dungeon_templates import *
from .dungeon_manager import DungeonManager
from .special_events import VillainHideout, LostItem, ForbiddingDoor, UnderdarkEntrance, DungeonEntrance
from treasure.treasure_api import RawHoardSource
from random import Random

template_lookup = {
'haunted_tomb': HauntedTombTemplate, 
'passing_ages': PassingAgesTemplate, 
'explorers': ExplorerTemplate,
'lair': LairTemplate,
'fungal_infection': FungalInfectionTemplate,
'stronghold': AbandonedStrongholdTemplate, 
'tree_choked': TreeChokedTemplate, 
'volcanic': VolcanicTemplate,
'treasure_vault': GuardedTreasureVaultTemplate,
'mine': AbandonedMineTemplate, 
'temple_remnants': AncientRemnantsTempleTemplate, 
'temple_in_use': InUseTempleTemplate,
'infested': InfestedTemplate,
'cave': InfestedCaveTemplate,
'villain_hideout': VillainHideout, 
'lost_item': LostItem, 
'underdark_entrance': UnderdarkEntrance,
'deep_cave': DeepCaveTemplate
}

class DungeonSource():
    def __init__(self, level, terrain=None, templates=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        layout = DungeonLayout(n_rooms=self.random_state.randint(4, 7), random_state=self.random_state)
        if templates is None:
            templates = [(template, None) for template in self.random_state.choice(some_examples)] + self.special_events()
        else:
            templates = self.translate_templates(templates)
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

    def special_events(self):
        special_events = []
        if self.random_state.randint(1, 6) >= 5:
            n_events = self.random_state.choice([1, 1, 1, 2])
            events = self.random_state.sample([UnderdarkEntrance, VillainHideout, LostItem, ForbiddingDoor, DungeonEntrance],n_events)
            special_events += events
        return [(i, None) for i in special_events]

    def translate_templates(self, template_list):
        templates = []
        for template in template_list:
            if ':' in template:
                name, monster_set = template.split(':')
            else:
                name = template
                monster_set = None
            templates.append((template_lookup[name], monster_set))
        return templates
            



