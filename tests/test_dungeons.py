from dungeons.dungeon_layout import DungeonLayout
from dungeons.dungeon_furnisher import DungeonFurnisher
from dungeons.dungeon_populator import OriginalInhabitants, UndergroundNatives, Lair, Explorers
from dungeons.dungeon_ager import DungeonAger
from dungeons.dungeon import Dungeon
from dungeons.dungeon_manager import DungeonManager, TreasureManager
from dungeons.dungeon_templates import *
from random import Random
from mocks.mock_dungeon_layout import MockDungeonLayout
from mocks.mock_encounter_source import MockEncounterSource
from mocks.mock_treasure_source import MockTreasureSource, MockRawHoardSource
from mocks.mock_monster_list import MockMonsterManual
from mocks.mock_trap_source import MockTrapSource
from mocks.mock_encounter_source import MockDungeonManager
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

def test_dungeon_layout_adds_distances():
    state = Random(0)
    n_rooms = 6
    connectivity_threshold = 1.2
    layout = DungeonLayout(n_rooms, connectivity_threshold, random_state=state)
    assert [n['distance'] for a, n in layout.nodes(data=True)] == [1, 2, 3, 4, 3, 5]


def test_dungeon_furnisher_loads_rooms():
    furnisher = DungeonFurnisher('stronghold')
    assert len(furnisher.room_type_list) > 0

def test_dungeon_furnisher_adds_descriptions():
    layout = MockDungeonLayout()
    state = Random(0)
    furnisher = DungeonFurnisher('stronghold', random_state=state)
    furnished = furnisher.furnish(layout)
    assert furnished.nodes(data=True)[0]['description'] == 'A wide spiralling staircase with many landings and branching corridors.'

def test_dungeon_furnisher_suitable_rooms():
    state = Random(0)
    furnisher = DungeonFurnisher('stronghold', random_state=state)
    # print(furnisher.suitable_rooms(['secret', 'something else']))

def test_dungeon_populator_adds_encounters():
    layout = MockDungeonLayout()
    manager = MockDungeonManager()
    state = Random(0)
    populator = OriginalInhabitants(dungeon_manager=manager, random_state=state)
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
    manager = MockDungeonManager()
    ager.age(layout)
    populator = UndergroundNatives(dungeon_manager=manager, random_state=state)
    populator.populate(layout)
    # for node, data in layout.nodes(data=True):
    #     print(data.get('encounter'), data.get('tags'))

def test_original_inhabitants():
    layout = MockDungeonLayout()
    state = Random(0)
    manager = MockDungeonManager()
    trap_source = MockTrapSource()
    populator = OriginalInhabitants(dungeon_manager=manager, trap_source=trap_source, random_state=state)
    populator.populate(layout)
    dungeon = Dungeon(layout)
    #print(dungeon.module()['rooms'])

def test_lair():
    layout = MockDungeonLayout()
    state = Random(0)
    manager = MockDungeonManager()
    populator = Lair(dungeon_manager=manager, random_state=state)
    populator.populate(layout)
    # for node, data in layout.nodes(data=True):
    #     print(data.get('encounter'), data.get('tags'))

def test_explorers():
    layout = MockDungeonLayout()
    state = Random(0)
    manager = MockDungeonManager()
    populator = Explorers(dungeon_manager=manager, random_state=state)
    populator.populate(layout)
    # for node, data in layout.nodes(data=True):
    #     print(data.get('encounter'), data.get('treasure'))


def test_taint():
    layout = MockDungeonLayout()
    state = Random(0)
    manager = MockDungeonManager()
    layout.node[0]['tags'] = ['populate']
    manager = MockDungeonManager()
    populator = Taint(dungeon_manager=manager, random_state=state)
    populator.populate(layout, tag='populate')
#     for node, data in layout.nodes(data=True):
#         print(data.get('encounter'), data.get('treasure'))

def test_dungeon_templates():
    layout = MockDungeonLayout()
    layout.purpose = 'temple'
    manager = MockDungeonManager()
    state = Random()
    template =  HauntedTemplate(1, dungeon_manager=manager)
    template.alter_dungeon(layout)
    # print(template.get_monster_sets())
    # for node, data in layout.nodes(data=True):
    #   print(data, '\n')


def test_populator_uses_treasure_source():
    layout = MockDungeonLayout()
    layout.purpose = 'temple'
    state = Random()
    manager=MockDungeonManager()
    template = GuardedTreasureVaultTemplate(1, dungeon_manager=manager)
    template.alter_dungeon(layout)
#     for node, data in layout.nodes(data=True):
#         print(data.get('treasure'), '\n')

def test_module_orders_rooms_correctly():
    state = Random(0)
    layout = DungeonLayout(5, random_state=state)
    layout.purpose = 'temple'
    dungeon = Dungeon(layout)
    assert dungeon.get_room_ids() == {0: 1, 3: 2, 2: 3, 4: 4, 1: 5}

def test_integration_from_encounter_manager_to_populator():
    layout = MockDungeonLayout()
    layout.purpose = 'temple'
    with DungeonManager(1, layout) as manager:
        template = AncientRemnantsTempleTemplate(4, dungeon_manager=manager)
        template.alter_dungeon(layout)
        # print(manager.encounters)

def test_manager_adds_encounters():
    state = Random(0)
    source = MockEncounterSource()
    layout = MockDungeonLayout()
    manager = DungeonManager(1, layout)
    manager.add_encounter_source('test', source)
    encounter = manager.get_encounter('test', style='test style')
    assert encounter['source name'] == 'test'
    assert encounter['style'] == 'test style'
    assert manager.encounters['test'] == 1

def test_manager_deletes_encounters():
    state = Random(0)
    source = MockEncounterSource()
    layout = MockDungeonLayout()
    manager = DungeonManager(1, layout)
    manager.add_encounter_source('test', source)
    encounter = manager.get_encounter('test', style='test style')
    assert manager.encounters['test'] == 1
    manager.delete_encounter(encounter)
    assert manager.encounters['test'] == 0

def test_manager_adds_events():
    state = Random(0)
    source = MockEncounterSource()
    layout = MockDungeonLayout()
    manager = DungeonManager(1, layout)
    with DungeonManager(1, layout) as manager:
        template = AncientRemnantsTempleTemplate(4, dungeon_manager=manager, random_state=state)
        template.alter_dungeon(layout)
    assert layout.events[0] == 'Echoes of the former worship still remain: (elemental plane of fire)'

def test_manager_only_shows_events_if_there_are_encounters():
    state = Random(0)
    source = MockEncounterSource()
    layout = MockDungeonLayout()
    manager = DungeonManager(1, layout)
    with DungeonManager(1, layout) as manager:
        template = AncientRemnantsTempleTemplate(4, dungeon_manager=manager)
        template.alter_dungeon(layout)
        manager.encounters[template.name] = 0
    assert layout.events == []

def test_manager_gets_signs():
    state = Random(0)
    source = MockEncounterSource()
    layout = MockDungeonLayout()
    manager = DungeonManager(1, layout)
    manager.add_encounter_source('test', source)
    sign = manager.get_sign('test')
    assert str(sign) == 'a sign of some scary monsters'

def test_manager_deletes_signs():
    state = Random(0)
    source = MockEncounterSource()
    layout = MockDungeonLayout()
    manager = DungeonManager(1, layout)
    manager.add_encounter_source('test', source)
    sign = manager.get_sign('test')
    manager.delete_signs('test')
    assert str(manager.signs['test'][0]) == ''

def test_deleting_encounters_deletes_signs():
    state = Random(0)
    source = MockEncounterSource()
    layout = MockDungeonLayout()
    with DungeonManager(1, layout) as manager:
        manager.add_encounter_source('test', source)
        encounter = manager.get_encounter('test')
        sign = manager.get_sign('test')
        # print(sign)
        manager.delete_encounter(encounter)
    # print(sign)

def test_deleting_different_encounters_deletes_signs():
    state = Random(0)
    layout = MockDungeonLayout()
    source = MockEncounterSource()
    with DungeonManager(1, layout) as manager:
        manager.add_encounter_source('test', source)
        manager.add_encounter_source('test_2', source)
        encounter = manager.get_encounter('test')
        encounter_2 = manager.get_encounter('test_2')
        sign = manager.get_sign('test')
        # print(sign)
        manager.delete_encounter(encounter)
        # print(manager.encounters)
    # print(sign)
    
def test_treasure_manager_makes_treasure():
    state = Random(0)
    source = MockRawHoardSource()
    items = source.get_treasure()
    manager = TreasureManager(items)
    treasure = manager.get_treasure(1)
    assert sorted(treasure.items) == sorted(items)

def test_treasure_manager_assigns_all_items_by_share():
    state = Random(0)
    source = MockRawHoardSource()
    items = source.get_treasure()
    manager = TreasureManager(items, random_state=state)
    treasure = manager.get_treasure(1)
    other_treasure = manager.get_treasure(2)
    assert sorted(treasure.items + other_treasure.items) == sorted(items)
    assert len(treasure.items) < len(other_treasure.items)
    #print(treasure.items)

def test_treasure_manager_deletes_treasures():
    state = Random(0)
    source = MockRawHoardSource()
    items = source.get_treasure()
    manager = TreasureManager(items, random_state=state)
    treasure = manager.get_treasure(1)
    assert sorted(treasure.items) == sorted(items)
    other_treasure = manager.get_treasure(2)
    assert sorted(treasure.items) != sorted(items)
    manager.delete_treasure(other_treasure)
    assert sorted(treasure.items) == sorted(items)

def test_treasures_look_nice():
    state = Random(0)
    source = MockRawHoardSource()
    items = source.get_treasure()
    manager = TreasureManager(items, random_state=state)
    treasure = manager.get_treasure(1)
    # print(treasure)

def test_delete_last_treasure():
    state = Random(0)
    source = MockRawHoardSource()
    items = source.get_treasure()
    manager = TreasureManager(items, random_state=state)
    treasure = manager.get_treasure(1)
    manager.delete_treasure(treasure)
