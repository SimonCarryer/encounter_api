from dungeons.special_events import VillainHideout
from mocks.mock_dungeon_layout import MockDungeonLayout
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

