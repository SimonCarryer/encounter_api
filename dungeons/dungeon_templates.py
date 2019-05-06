from .dungeon_populator import Lair, OriginalInhabitants, UndergroundNatives, Explorers, Taint
from .dungeon_ager import DungeonAger
from encounters.encounter_api import EncounterSource
from treasure.treasure_api import HoardSource, NothingSource
from .dungeon_furnisher import DungeonFurnisher
from .dungeon_manager import DungeonManager
from random import Random
import yaml
import uuid
from utils.library import monster_manual, use_real_monster_manual
from traps.trap_api import TrapSource

with open('data/dungeon_age.yaml', 'r') as f:
    dungeon_age = yaml.load(f)
    effects = []
    for cause in dungeon_age.keys():
        for idx, room_effect in enumerate(dungeon_age[cause]['rooms']):
            effects.append(room_effect)

class NoEncountersSource:
    def __init__(self):
        self.monster_set = None

    def get_encounter(*args, **kwargs):
        return {'success': False}

    def get_sign(self, name=None):
        return 'The accumulated dust of many ages.' # TODO: Make this better.

class DungeonTemplate:
    def __init__(self, level, dungeon_manager=None, random_state=None, monster_set=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.dungeon_manager = dungeon_manager
        self.name = str(uuid.uuid4())
        self.monster_set = monster_set
        self.level = level

    def monster_sets(self, required_tags=None, none_tags=None, any_tags=None):
        if self.monster_set is None:
            sets = self.dungeon_manager.get_monster_sets(all_tags=required_tags, none_tags=none_tags, any_tags=any_tags, level=self.level)
            if len(sets) == 0:
                sets = self.dungeon_manager.get_monster_sets(all_tags=required_tags, none_tags=none_tags, any_tags=any_tags)
            return sets
        else:
            return [self.monster_set]

    def build_populator(self, monster_sets=None, populator_method=OriginalInhabitants, trap_source=None):
        if monster_sets is None:
            encounter_source = NoEncountersSource()
        else:
            encounter_source = EncounterSource(encounter_level=self.level,
                                                monster_sets=monster_sets,
                                                random_state=self.random_state)
        self.dungeon_manager.add_encounter_source(self.name, encounter_source)
        populator = populator_method(name=self.name,
                                     dungeon_manager=self.dungeon_manager,
                                     trap_source=trap_source,
                                     random_state=self.random_state)
        self.dungeon_manager.add_event(self.name, self.event_type(), encounter_source.monster_set)
        return populator
    
    def build_ager(self, cause):
        return DungeonAger(cause=cause, random_state=self.random_state)

    def event_type(self):
        return 'Home to some scary monsters'

class DungeonBaseTemplate(DungeonTemplate):
    def event_type(self):
        return 'Guarded by remnants of the original inhabitants'

    def build_furnisher(self, dungeon_type):
        return DungeonFurnisher(dungeon_type, random_state=self.random_state)

class NewInhabitantsTemplate(DungeonTemplate):
    def event_type(self):
        return 'Now home to new creatures'

    def free_rooms(self, layout):
        return [room for room, data in layout.nodes(data=True) if 'uninhabitable' not in data['tags']]

    def free_entrances(self, layout, tag='entrance'):
        return [room for room, data in layout.nodes(data=True) if tag in data['tags'] and 'uninhabitable' not in data['tags']]

    def make_an_entrace(self, layout, tag='entrance'):
        if len(self.free_entrances(layout, tag=tag)) == 0:
            free_rooms = self.free_rooms(layout)
            if len(free_rooms) > 0:
                new_entrance = self.random_state.choice(free_rooms)
                entrance_effects = [effect for effect in effects if tag in effect.get('tags', [])]
                effect = self.random_state.choice(entrance_effects)
                layout.node[new_entrance]['tags'] += [tag]
                current_description = layout.node[new_entrance].get('description', '')
                layout.node[new_entrance]['description'] = ' '.join([current_description, effect['description']])

class HauntedTombTemplate(DungeonBaseTemplate):
    def event_type(self):
        return 'Haunted by the unquiet dead'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['undead', 'immortal', 'guardian'])

    def alter_dungeon(self, layout):
        self.build_furnisher('tomb').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator(self.get_monster_sets(), trap_source=trap_source).populate(layout)
        return layout

class AbandonedStrongholdTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher('stronghold').furnish(layout)
        trap_source = TrapSource(self.level, trap_class='mechanical', random_state=self.random_state)
        populator = self.build_populator(monster_sets=None, trap_source=trap_source)
        populator.populate(layout)
        return layout

class GuardedTreasureVaultTemplate(DungeonBaseTemplate):
    def event_type(self):
        return 'Still guarded by ancient wards'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['immortal', 'guardian'], none_tags=['undead'])

    def alter_dungeon(self, layout):
        self.build_furnisher('treasure vault').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator(self.get_monster_sets(), trap_source=trap_source).populate(layout)
        return layout

class AbandonedMineTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher('mine').furnish(layout)
        return layout

class AncientRemnantsTempleTemplate(DungeonBaseTemplate):
    def event_type(self):
        return 'Echoes of the former worship still remain'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['immortal'], any_tags=['evil', 'magical'], none_tags=['underdark'])
    
    def alter_dungeon(self, layout):
        self.build_furnisher('temple').furnish(layout)
        trap_source = TrapSource(self.level, trap_class='magical')
        self.build_populator(self.get_monster_sets(), trap_source=trap_source).populate(layout)
        return layout

class InUseTempleTemplate(DungeonBaseTemplate):
    def event_type(self):
        return 'Protected by fanatical worshipers'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['humanoid'], any_tags=['evil', 'magical'], none_tags=['underdark'])

    def alter_dungeon(self, layout):
        self.build_furnisher('temple').furnish(layout)
        trap_source = TrapSource(self.level)
        self.build_populator(self.get_monster_sets(), trap_source=trap_source).populate(layout)
        return layout

class InfestedCaveTemplate(DungeonBaseTemplate):
    def event_type(self):
        return 'Home to cave-dwelling creatures'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['cave-dweller'], none_tags=['rare', 'underdark'])

    def alter_dungeon(self, layout):
        self.build_furnisher('cave').furnish(layout)
        self.build_ager(cause='cave-age').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=UndergroundNatives).populate(layout)
        return layout

class HauntedTemplate(DungeonTemplate):
    def event_type(self):
        return 'Haunted by ghosts of the past'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['undead'], none_tags=['guardian'])
    
    def alter_dungeon(self, layout):
        self.build_ager('shadowfell').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Taint).populate(layout, tag='shadowfell')
        return layout

class TreeChokedTemplate(DungeonTemplate):
    def event_type(self):
        return 'Overgrown by evil-tainted forest'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['plant'])

    def alter_dungeon(self, layout):
        self.build_ager('trees').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Taint).populate(layout, tag='trees')
        return layout

class FungalInfectionTemplate(DungeonTemplate):
    def event_type(self):
        return 'Overgrown with weird fungi'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['fungus', 'cave-dweller'])

    def alter_dungeon(self, layout):
        self.build_ager('fungus').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Taint).populate(layout, tag='fungus')
        return layout

class VolcanicTemplate(DungeonTemplate):
    def event_type(self):
        return 'Near-destroyed by volcanic activity'

    def get_monster_sets(self):
        return self.monster_sets(required_tags=['fire'])

    def alter_dungeon(self, layout):
        self.build_ager('volcano').age(layout)
        self.build_populator(self.get_monster_sets(), populator_method=Taint).populate(layout, tag='fire')
        return layout

class InfestedTemplate(NewInhabitantsTemplate):
    def event_type(self):
        return 'Infested with subterranean fauna'

    def alter_dungeon(self, layout):
        monster_sets = self.monster_sets(required_tags=['cave-dweller'], none_tags=['underdark', 'rare'])
        age_effect = self.random_state.choice(['earthquake', 'flood', 'age'])
        self.build_ager(age_effect).age(layout)
        self.make_an_entrace(layout, tag='cave-entrance')
        self.build_populator(monster_sets, populator_method=UndergroundNatives).populate(layout)
        return layout

class LairTemplate(NewInhabitantsTemplate):
    def event_type(self):
        return 'Inhabited by beasts from the surrounding area'

    def alter_dungeon(self, layout):
        self.make_an_entrace(layout)
        monster_sets = self.monster_sets(required_tags=['beast'], none_tags=['underdark'])
        self.build_populator(monster_sets, populator_method=Lair).populate(layout)
        return layout

class ExplorerTemplate(NewInhabitantsTemplate):
    def event_type(self):
        return 'A lair for marauders and savages'

    def get_monster_sets(self, layout):
        none_tags = ['evil', 'underdark']
        if layout.purpose == 'temple':
            none_tags = ['underdark']
        return self.monster_sets(required_tags=['dungeon-explorer'], none_tags=none_tags)

    def alter_dungeon(self, layout):
        self.make_an_entrace(layout)
        self.build_populator(self.get_monster_sets(layout), populator_method=Explorers).populate(layout)
        return layout

class PassingAgesTemplate(DungeonTemplate):

    def alter_dungeon(self, layout):
        age_effect = self.random_state.choice(['earthquake', 'flood', 'age', 'fungus', 'trees'])
        self.build_ager(cause=age_effect).age(layout)

some_examples = [
[HauntedTombTemplate, PassingAgesTemplate, ExplorerTemplate],
[HauntedTombTemplate, PassingAgesTemplate, LairTemplate, ExplorerTemplate],
[HauntedTombTemplate, FungalInfectionTemplate, LairTemplate, ExplorerTemplate],
[HauntedTombTemplate, PassingAgesTemplate],
[AbandonedStrongholdTemplate, HauntedTemplate, LairTemplate],
[AbandonedStrongholdTemplate, HauntedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, InfestedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, TreeChokedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, InfestedTemplate, LairTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, FungalInfectionTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, VolcanicTemplate],
[GuardedTreasureVaultTemplate, PassingAgesTemplate, ExplorerTemplate],
[GuardedTreasureVaultTemplate, PassingAgesTemplate, LairTemplate],
[GuardedTreasureVaultTemplate, InfestedTemplate],
[AbandonedMineTemplate, InfestedTemplate, ExplorerTemplate],
[AbandonedMineTemplate, VolcanicTemplate, ExplorerTemplate],
[AbandonedMineTemplate, InfestedTemplate, LairTemplate],
[AbandonedMineTemplate, PassingAgesTemplate, FungalInfectionTemplate, LairTemplate],
[AncientRemnantsTempleTemplate, PassingAgesTemplate, ExplorerTemplate],
[AncientRemnantsTempleTemplate, InfestedTemplate, LairTemplate],
[InUseTempleTemplate],
[InfestedCaveTemplate, ExplorerTemplate],
[InfestedCaveTemplate, VolcanicTemplate],
[InfestedCaveTemplate, TreeChokedTemplate],
[InfestedCaveTemplate, LairTemplate, ExplorerTemplate],
[InfestedCaveTemplate, FungalInfectionTemplate, ExplorerTemplate],
[InfestedCaveTemplate, LairTemplate, LairTemplate]
]