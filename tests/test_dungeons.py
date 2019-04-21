from dungeons.dungeon_layout import DungeonLayout
from dungeons.dungeon_furnisher import DungeonFurnisher
from dungeons.dungeon_populator import OriginalInhabitants, UndergroundNatives, Lair, Explorers
from dungeons.dungeon_ager import DungeonAger
from dungeons.dungeon import Dungeon
from dungeons.dungeon_templates import *
from random import Random
from mocks.mock_dungeon_layout import MockDungeonLayout
from mocks.mock_encounter_source import MockEncounterSource
from mocks.mock_treasure_source import MockTreasureSource
from mocks.mock_monster_list import MockMonsterManual
from utils import library

def test_dungeon_layout_has_correct_number_of_rooms():
    state = Random(0)
    n_rooms = 6
    connectivity_threshold = 1.2
    layout = DungeonLayout(n_rooms, connectivity_threshold, random_state=state)
    assert len(layout.nodes()) == 6

def test_dungeon_layout_tags_nodes():
    state = Random(0)
    n_rooms = 6
    connectivity_threshold = 1.2
    layout = DungeonLayout(n_rooms, connectivity_threshold, random_state=state)
    assert layout.nodes(data=True)[0]['tags'][0] == 'entrance'

def test_dungeon_furnisher_loads_rooms():
    furnisher = DungeonFurnisher('stronghold')
    assert len(furnisher.room_type_list) > 0

def test_dungeon_furnisher_adds_descriptions():
    layout = MockDungeonLayout()
    state = Random(0)
    furnisher = DungeonFurnisher('stronghold', random_state=state)
    furnished = furnisher.furnish(layout)
    assert furnished.nodes(data=True)[0]['description'] == 'Guardroom.'


def test_dungeon_populator_adds_encounters():
    layout = MockDungeonLayout()
    encounter_source = MockEncounterSource()
    treasure_source = MockTreasureSource()
    state = Random(0)
    populator = OriginalInhabitants(encounter_source, treasure_source, random_state=state)
    populator.populate(layout)
    # for node, data in layout.nodes(data=True):
    #      print(data.get('encounter'))

def test_dungeon_ager_ages_dungeon():
    layout = MockDungeonLayout()
    state = Random(0)
    furnisher = DungeonFurnisher('stronghold', random_state=state)
    ager = DungeonAger('age', random_state=state)
    furnisher.furnish(layout)
    ager.age(layout)
#     for node, data in layout.nodes(data=True):
#         print(data.get('description'), data.get('tags'))
#     for start, end, data in layout.edges(data=True):
#         print(data.get('description'))

def test_dungeon_ager_adds_tags():
    layout = MockDungeonLayout()
    state = Random(0)
    furnisher = DungeonFurnisher('stronghold', random_state=state)
    ager = DungeonAger('shadowfell', random_state=state)
    ager.age(layout)
#     for node, data in layout.nodes(data=True):
#         print(data.get('tags'))

def test_underground_natives():
    layout = MockDungeonLayout()
    state = Random(0)
    ager = DungeonAger('age', random_state=state)
    encounter_source = MockEncounterSource()
    treasure_source = MockTreasureSource()
    ager.age(layout)
    populator = UndergroundNatives(encounter_source, treasure_source, random_state=state)
    populator.populate(layout)
    # for node, data in layout.nodes(data=True):
    #     print(data.get('encounter'), data.get('tags'))

def test_lair():
    layout = MockDungeonLayout()
    state = Random(0)
    encounter_source = MockEncounterSource()
    treasure_source = MockTreasureSource()
    populator = Lair(encounter_source, treasure_source, random_state=state)
    populator.populate(layout)
    # for node, data in layout.nodes(data=True):
    #     print(data.get('encounter'), data.get('tags'))

def test_explorers():
    layout = MockDungeonLayout()
    state = Random(0)
    encounter_source = MockEncounterSource()
    treasure_source = MockTreasureSource()
    populator = Explorers(encounter_source, treasure_source, random_state=state)
    populator.populate(layout)
    # for node, data in layout.nodes(data=True):
    #     print(data.get('encounter'), data.get('treasure'))


def test_taint():
    layout = MockDungeonLayout()
    state = Random(0)
    encounter_source = MockEncounterSource()
    treasure_source = MockTreasureSource()
    layout.node[0]['tags'] = ['populate']
    populator = Taint(encounter_source, treasure_source, random_state=state)
    populator.populate(layout, tag='populate')
#     for node, data in layout.nodes(data=True):
#         print(data.get('encounter'), data.get('treasure'))

def test_dungeon_templates():
    layout = MockDungeonLayout()
    layout.purpose = 'temple'
    state = Random()
    template =  HauntedTemplate(1)
    template.alter_dungeon(layout)
    # print(template.get_monster_sets())
    # for node, data in layout.nodes(data=True):
    #   print(data, '\n')
