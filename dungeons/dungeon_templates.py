from .dungeon_populator import Lair, OriginalInhabitants, UndergroundNatives, Explorers, Taint
from .dungeon_ager import DungeonAger
from encounters.encounter_api import EncounterSource
from treasure.treasure_api import HoardSource, NothingSource
from .dungeon_furnisher import DungeonFurnisher
from random import Random
import yaml
from utils.library import monster_manual, use_real_monster_manual

with open('data/dungeon_age.yaml', 'r') as f:
    dungeon_age = yaml.load(f)
    effects = []
    for cause in dungeon_age.keys():
        for idx, room_effect in enumerate(dungeon_age[cause]['rooms']):
            effects.append(room_effect)

class DungeonTemplate:
    def __init__(self, level, monster_set=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.monster_set = monster_set
        self.level = level

    def monster_sets(self, required_tags=None, none_tags=None, any_tags=None):
        if self.monster_set is None:
            sets = monster_manual.get_monster_sets(all_tags=required_tags, none_tags=none_tags, any_tags=any_tags, level=self.level)
            if len(sets) == 0:
                sets = monster_manual.get_monster_sets(all_tags=required_tags, none_tags=none_tags, any_tags=any_tags)
            return sets
        else:
            return [self.monster_set]
    
class DungeonBaseTemplate(DungeonTemplate):
    def build_populator(self, monster_sets):
        encounter_source = EncounterSource(encounter_level=self.level,
                                            monster_sets=monster_sets,
                                            random_state=self.random_state)
        treasure_source = HoardSource(encounter_level=self.level,
                                            random_state=self.random_state)
        return OriginalInhabitants(encounter_source, treasure_source, random_state=self.random_state)

    def build_furnisher(self, dungeon_type):
        return DungeonFurnisher(dungeon_type, random_state=self.random_state)

class DungeonTaintTemplate(DungeonTemplate):
    def build_ager(self, ager_type):
        return DungeonAger(cause=ager_type, random_state=self.random_state)

    def build_populator(self, monster_sets):
        encounter_source = EncounterSource(encounter_level=self.level,
                                            monster_sets=monster_sets,
                                            random_state=self.random_state)
        treasure_source = HoardSource(encounter_level=self.level,
                                            random_state=self.random_state)
        return Taint(encounter_source, treasure_source, random_state=self.random_state)

class NewInhabitantsTemplate(DungeonTemplate):
    def free_rooms(self, layout):
        return [room for room, data in layout.nodes(data=True) if 'uninhabitable' not in data['tags']]

    def free_entrances(self, layout, tag='entrance'):
        return [room for room, data in layout.nodes(data=True) if tag in data['tags'] and 'uninhabitable' not in data['tags']]

    def make_an_entrace(self, layout, tag='entrance'):
        if len(self.free_entrances(layout, tag=tag)) == 0:
            new_entrance = self.random_state.choice(self.free_rooms(layout))
            entrance_effects = [effect for effect in effects if tag in effect.get('tags', [])]
            effect = self.random_state.choice(entrance_effects)
            layout.node[new_entrance]['tags'] += [tag]
            current_description = layout.node[new_entrance].get('description', '')
            layout.node[new_entrance]['description'] = ' '.join([current_description, effect['description']])

    def build_ager(self, ager_type):
        return DungeonAger(cause=ager_type, random_state=self.random_state)

    def build_populator(self, monster_sets, method, treasure=HoardSource):
        encounter_source = EncounterSource(encounter_level=self.level,
                                            monster_sets=monster_sets,
                                            random_state=self.random_state)
        treasure_source = treasure(encounter_level=self.level,
                                            random_state=self.random_state)
        return method(encounter_source, treasure_source, random_state=self.random_state)

class DungeonAgeTemplate(DungeonTemplate):
    def build_ager(self, ager_type):
        return DungeonAger(cause=ager_type, random_state=self.random_state)

class HauntedTombTemplate(DungeonBaseTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['undead', 'immortal', 'guardian'])

    def alter_dungeon(self, layout):
        self.build_furnisher('tomb').furnish(layout)
        self.build_populator(self.get_monster_sets()).populate(layout)
        return layout

class AbandonedStrongholdTemplate(DungeonBaseTemplate):    
    def alter_dungeon(self, layout):
        self.build_furnisher('stronghold').furnish(layout)
        return layout

class GuardedTreasureVaultTemplate(DungeonBaseTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['immortal', 'guardian'], none_tags=['undead'])

    def alter_dungeon(self, layout):
        self.build_furnisher('treasure vault').furnish(layout)
        self.build_populator(self.get_monster_sets()).populate(layout)
        return layout

class AbandonedMineTemplate(DungeonBaseTemplate):
    def alter_dungeon(self, layout):
        self.build_furnisher('mine').furnish(layout)
        return layout

class AncientRemnantsTempleTemplate(DungeonBaseTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['immortal'], any_tags=['evil', 'magical'])
    
    def alter_dungeon(self, layout):
        self.build_furnisher('temple').furnish(layout)
        self.build_populator(self.get_monster_sets()).populate(layout)
        return layout

class InUseTempleTemplate(DungeonBaseTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['humanoid'], any_tags=['evil', 'magical'])

    def alter_dungeon(self, layout):
        self.build_furnisher('temple').furnish(layout)
        self.build_populator(self.get_monster_sets()).populate(layout)
        return layout

class InfestedCaveTemplate(DungeonBaseTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['cave-dweller'], none_tags=['underdark'])

    def alter_dungeon(self, layout):
        self.build_furnisher('cave').furnish(layout)
        self.build_populator(self.get_monster_sets()).populate(layout)
        self.build_ager().age(layout)
        return layout

    def build_ager(self):
        return DungeonAger(cause='cave-age', random_state=self.random_state)

    def build_populator(self, monster_sets):
        encounter_source = EncounterSource(encounter_level=self.level,
                                            monster_sets=monster_sets,
                                            random_state=self.random_state)
        treasure_source = NothingSource(encounter_level=self.level,
                                            random_state=self.random_state)
        return OriginalInhabitants(encounter_source, treasure_source, random_state=self.random_state)

class HauntedTemplate(DungeonTaintTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['undead'], none_tags=['guardian'])
    
    def alter_dungeon(self, layout):
        self.build_ager('shadowfell').age(layout)
        self.build_populator(self.get_monster_sets()).populate(layout, tag='shadowfell')
        return layout

class TreeChokedTemplate(DungeonTaintTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['plant'])

    def alter_dungeon(self, layout):
        self.build_ager('trees').age(layout)
        self.build_populator(self.get_monster_sets()).populate(layout, tag='trees')
        return layout

class FungalInfectionTemplate(DungeonTaintTemplate):
    def get_monster_sets(self):
        return self.monster_sets(required_tags=['fungus', 'cave-dweller'])

    def alter_dungeon(self, layout):
        self.build_ager('fungus').age(layout)
        self.build_populator(self.get_monster_sets()).populate(layout, tag='fungus')
        return layout

class InfestedTemplate(NewInhabitantsTemplate):
    def alter_dungeon(self, layout):
        monster_sets = self.monster_sets(required_tags=['cave-dweller'], none_tags=['underdark'])
        age_effect = self.random_state.choice(['earthquake', 'flood', 'age'])
        self.build_ager(age_effect).age(layout)
        self.make_an_entrace(layout, tag='cave-entrance')
        self.build_populator(monster_sets, UndergroundNatives, treasure=NothingSource).populate(layout)
        self.make_an_entrace(layout, tag='cave-entrance')
        self.build_populator(monster_sets, UndergroundNatives, treasure=NothingSource).populate(layout)
        return layout

class LairTemplate(NewInhabitantsTemplate):
    def alter_dungeon(self, layout):
        self.make_an_entrace(layout)
        monster_sets = self.monster_sets(required_tags=['beast'], any_tags=['forest', 'mountains', 'desert', 'plains', 'swamp', 'arctic'])
        self.build_populator(monster_sets, Lair).populate(layout)
        return layout

class ExplorerTemplate(NewInhabitantsTemplate):
    def get_monster_sets(self, layout):
        none_tags = ['evil']
        if layout.purpose == 'temple':
            none_tags = None
        return self.monster_sets(required_tags=['dungeon-explorer'], none_tags=none_tags)

    def alter_dungeon(self, layout):
        self.make_an_entrace(layout)
        self.build_populator(self.get_monster_sets(layout), Explorers).populate(layout)
        return layout

class PassingAgesTemplate(DungeonAgeTemplate):
    def alter_dungeon(self, layout):
        age_effect = self.random_state.choice(['earthquake', 'flood', 'age', 'fungus', 'trees'])
        self.build_ager(age_effect).age(layout)

some_examples = [
[HauntedTombTemplate, PassingAgesTemplate, ExplorerTemplate],
[HauntedTombTemplate, PassingAgesTemplate, LairTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, HauntedTemplate, LairTemplate],
[AbandonedStrongholdTemplate, HauntedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, InfestedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, TreeChokedTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, InfestedTemplate, LairTemplate, ExplorerTemplate],
[AbandonedStrongholdTemplate, FungalInfectionTemplate, ExplorerTemplate],
[GuardedTreasureVaultTemplate, PassingAgesTemplate, ExplorerTemplate],
[GuardedTreasureVaultTemplate, PassingAgesTemplate, LairTemplate],
[GuardedTreasureVaultTemplate, InfestedTemplate],
[AbandonedMineTemplate, InfestedTemplate, ExplorerTemplate],
[AbandonedMineTemplate, InfestedTemplate, LairTemplate],
[AbandonedMineTemplate, PassingAgesTemplate, FungalInfectionTemplate, LairTemplate],
[AncientRemnantsTempleTemplate, PassingAgesTemplate, ExplorerTemplate],
[AncientRemnantsTempleTemplate, InfestedTemplate, LairTemplate],
[InUseTempleTemplate],
[InfestedCaveTemplate, ExplorerTemplate],
[InfestedCaveTemplate, LairTemplate, ExplorerTemplate],
[InfestedCaveTemplate, FungalInfectionTemplate, ExplorerTemplate],
[InfestedCaveTemplate, PassingAgesTemplate, LairTemplate]
]
