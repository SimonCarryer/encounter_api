from dungeons.special_events import VillainHideout, DungeonEntrance, DragonLair, TrapRoom
from mocks.mock_dungeon_layout import MockDungeonLayout
from mocks.mock_encounter_source import MockDungeonManager
from dungeons.dungeon_manager import DungeonManager


def test_villain_hideout_gets_villains():
    event = VillainHideout(5, None)
    # print(event.get_villain())

def test_villain_hideout_chooses_good_room():
    layout = MockDungeonLayout()
    event = VillainHideout(5, None)
    assert event.find_best_room(layout) == 4

def test_villain_hideout_integration():
    layout = MockDungeonLayout()
    with DungeonManager(5, layout) as manager:
        event = VillainHideout(5, manager)
        event.alter_dungeon(layout)
    # for node, data in layout.nodes(data=True):
    #     print(data.get('encounter'))
    # print(layout.events)

def test_dungeon_entrance_get_url():
    layout = MockDungeonLayout()
    layout.terrain = 'hills'
    manager = MockDungeonManager()
    entrance = DungeonEntrance(1, manager)
    # print(entrance.dungeon_url(layout))

def test_trap_room_description():
    layout = MockDungeonLayout()
    layout.terrain = 'hills'
    manager = MockDungeonManager()
    room = TrapRoom(1, manager)
    # print(room.room_description())

# def test_lair_chooses_dragon():
#     layout = MockDungeonLayout()
#     with DungeonManager(5, layout) as manager:
#         event = DragonLair(5, manager)
#         print(event.choose_dragon())