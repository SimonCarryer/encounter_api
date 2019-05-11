from encounters.encounter_api import EncounterSource
from encounters.wandering_monsters import WanderingMonsters
from treasure.treasure_api import RawHoardSource
from monster_manual.monster_manual import MonsterManual
from names.name_api import NameGenerator
from random import Random


class Sign:
    def __init__(self, sign):
        self.sign = sign

    def __str__(self):
        if self.sign:
            return self.sign
        else:
            return ''

    def delete(self):
        self.sign = None

class Treasure(dict):
    def __init__(self, manager):
        self.manager = manager
        self.items = []
        self['coins'] = {}
        self['magic_items'] = []
        self['gemstones'] = []
        self['objects'] = []


    def get_item(self, item_type, item_value):
        self.items.append((item_type, item_value))
        if item_type == 'magic item':
            self['magic_items'].append(item_value)
        elif item_type in ['CP', 'SP', 'EP', 'GP', 'PP']:
            self['coins'][item_type] = item_value
        elif item_type == 'gem':
            self['gemstones'].append(item_value)
        else:
            self['objects'].append(item_value)
        
    def clear_items(self):
        self.items = []
        self['coins'] = {}
        self['magic_items'] = []
        self['gemstones'] = []
        self['objects'] = []


class TreasureManager:
    def __init__(self, list_of_things, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.list_of_things = list_of_things
        self.treasures = []
        self.shares = []

    def get_treasure(self, shares=1):
        treasure = Treasure(self)
        idx = len(self.shares)
        self.treasures.append(treasure)
        for _ in range(shares):
            self.shares.append(treasure)
        self.assign_items()
        return treasure
    
    def clear_all(self):
        for treasure in self.treasures:
            treasure.clear_items()

    def assign_items(self):
        self.clear_all()
        self.random_state.shuffle(self.shares)
        n_shares = len(self.shares)
        for idx, item in enumerate(self.list_of_things):
            self.shares[idx % n_shares].get_item(*item)

    def delete_treasure(self, treasure_to_delete):
        self.treasures = [treasure for treasure in self.treasures if treasure is not treasure_to_delete]
        self.shares = [share for share in self.shares if share is not treasure_to_delete]
        if len(self.treasures) > 0:
            self.assign_items()

class DungeonManager:
    def __init__(self, level, layout, terrain=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        self.layout = layout
        self.encounter_sources = {}
        self.encounters = {}
        self.signs = {}
        treasure = RawHoardSource(level, random_state=self.random_state).get_treasure()
        self.treasure_manager = TreasureManager(treasure, random_state=self.random_state)
        self.terrain = terrain
        self.monster_manual = MonsterManual(terrain=terrain)
        self.events = []
        self.name_generator = NameGenerator(random_state=self.random_state)
        self.wandering_monsters = {}

    def add_encounter_source(self, source_name, encounter_source):
        self.encounter_sources[source_name] = encounter_source
        self.encounters[source_name] = 0
        self.signs[source_name] = []

    def add_event(self, source_name, method_name, monster_set, wandering=False):
        event = {
            'event': method_name,
            'monster_set': monster_set,
            'source_name': source_name
        }
        self.events.append(event)
        if wandering:
            self.wandering_monsters[source_name] = monster_set

    def get_encounter(self, source_name, **kwargs):
        encounter = self.encounter_sources[source_name].get_encounter(**kwargs)
        if encounter.get('success'):
            self.encounters[source_name] += 1
            encounter['source name'] = source_name
            return encounter
        else:
            return None

    def delete_encounter(self, encounter):
        source_name = encounter.get('source name')
        self.encounters[source_name] -= 1

    def get_sign(self, source_name):
        sign = Sign(self.encounter_sources[source_name].get_sign())
        self.signs[source_name].append(sign)
        return sign

    def delete_signs(self, source_name):
        for sign in self.signs[source_name]:
            sign.delete()

    def __enter__(self, *args):
        return self

    def get_treasure(self, shares=1):
        return self.treasure_manager.get_treasure(shares)

    def delete_treasure(self, treasure_to_delete):
        self.treasure_manager.delete_treasure(treasure_to_delete)

    def get_monster_sets(self, **kwargs):
        return self.monster_manual.get_monster_sets(**kwargs)

    def parse_event(self, event):
        text = event['event']
        monster_set = event['monster_set']
        return f'{text}: ({monster_set})'

    def __exit__(self, eType, eValue, eTrace):
        for source_name in self.encounter_sources:
            if self.encounters[source_name] == 0:
                self.delete_signs(source_name)
        wandering = []
        for source_name, set_name in self.wandering_monsters.items():
            if self.encounters[source_name] > 0:
                wandering.append(set_name)
        self.layout.wandering_monster_table = WanderingMonsters(self.level, wandering, random_state=self.random_state).table
        self.layout.name = self.name_generator.dungeon_name(self.layout.purpose, terrain=self.terrain)
        self.layout.terrain = self.terrain
        self.layout.events = [self.parse_event(event) for event in self.events if event['source_name'] == 'special' or self.encounters[event['source_name']] > 0]

        