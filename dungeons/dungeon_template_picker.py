from .dungeon_templates import *
from .dungeon_manager import DungeonManager
from monster_manual.monster_manual import MonsterManual
from .special_events import VillainHideout, LostItem, ForbiddingDoor, UnderdarkEntrance, DungeonEntrance, WeirdEncounter, NPCHome

from random import Random

template_bunches = {
    'tomb': [[HauntedTombTemplate, PassingAgesTemplate, ExplorerTemplate],
[HauntedTombTemplate, PassingAgesTemplate, LairTemplate, ExplorerTemplate],
[HauntedTombTemplate, FungalInfectionTemplate, LairTemplate, ExplorerTemplate],
[HauntedTombTemplate, PassingAgesTemplate],
[EmptyTombTemplate, HauntedTemplate, PassingAgesTemplate],
[EmptyTombTemplate, PassingAgesTemplate, ExplorerTemplate],
[EmptyTombTemplate, PassingAgesTemplate, LairTemplate, ExplorerTemplate]],
    'stronghold': [[AbandonedStrongholdTemplate, HauntedTemplate, LairTemplate],
[AbandonedStrongholdTemplate, HauntedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, InfestedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, TreeChokedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, InfestedTemplate, LairTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, FungalInfectionTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, VolcanicTemplate],
[AbandonedStrongholdTemplate, HauntedTemplate, PassingAgesTemplate]],
    'treasure vault': [[GuardedTreasureVaultTemplate, PassingAgesTemplate, ExplorerTemplate],
[GuardedTreasureVaultTemplate, PassingAgesTemplate, LairTemplate],
[GuardedTreasureVaultTemplate, InfestedTemplate],
[GuardedTreasureVaultTemplate, PassingAgesTemplate, HauntedTemplate]],
    'mine': [[AbandonedMineTemplate, InfestedTemplate, ExplorerTemplate],
[AbandonedMineTemplate, VolcanicTemplate, ExplorerTemplate],
[AbandonedMineTemplate, InfestedTemplate, LairTemplate],
[AbandonedMineTemplate, PassingAgesTemplate, FungalInfectionTemplate, LairTemplate],
[AbandonedMineTemplate, HauntedTemplate]],
    'temple': [[AncientRemnantsTempleTemplate, PassingAgesTemplate, ExplorerTemplate],
[AncientRemnantsTempleTemplate, InfestedTemplate, LairTemplate],
[InUseTempleTemplate],
[AncientRemnantsTempleTemplate, HauntedTemplate]],
    'cave': [[InfestedCaveTemplate, InfestedTemplate],
[InfestedCaveTemplate, ExplorerTemplate],
[InfestedCaveTemplate, VolcanicTemplate],
[InfestedCaveTemplate, TreeChokedTemplate],
[InfestedCaveTemplate, LairTemplate, ExplorerTemplate],
[InfestedCaveTemplate, FungalInfectionTemplate, ExplorerTemplate],
[InfestedCaveTemplate, LairTemplate, LairTemplate]]
}

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

class TemplatePicker:
    def __init__(self, base_type, supplied_templates=None, supplied_monster_set=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        if base_type is None:
            self.base_type = random_state.choice(list(template_bunches.keys()))
        else:
            self.base_type = base_type
        self.supplied_templates = supplied_templates
        self.supplied_monster_set = supplied_monster_set

    def pick_set(self):
        if self.supplied_templates is not None:
            templates = self.translate_templates(self.supplied_templates)
        elif self.supplied_monster_set is not None:
            template_set = self.template_from_monster_set(self.supplied_monster_set)
            templates = [(template, None) for template in template_set[:-1]]
            templates += [(template_set[-1], self.supplied_monster_set)]
            templates += self.special_events()
        else:
            templates = [(template, None) for template in self.random_state.choice(template_bunches[self.base_type])] + self.special_events()
        return templates
        
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

    def special_events(self):
        special_events = []
        if self.random_state.randint(1, 6) >= 5:
            n_events = self.random_state.choice([1, 1, 1, 2])
            events = self.random_state.sample([NPCHome, WeirdEncounter, UnderdarkEntrance, VillainHideout, LostItem, ForbiddingDoor, DungeonEntrance],n_events)
            special_events += events
        return [(i, None) for i in special_events]

    def template_from_monster_set(self, monster_set):
        dummy_manager = MonsterManual()
        potentials = []
        for bunch in template_bunches[self.base_type]:
            sets = []
            i = 1
            while len(sets) == 0 and i <= len(bunch):
                template = bunch[-i]
                i += 1
                sets = template(None, dummy_manager, random_state=self.random_state).get_monster_sets()
                if monster_set in sets:
                    potentials.append(bunch)
        if len(potentials) > 0:
            return self.random_state.choice(potentials)
        else:
            sets = self.random_state.choice(template_bunches[self.base_type])
            if sets[-1] == ExplorerTemplate:
                return sets
            else:
                return sets + [ExplorerTemplate]

