from .dungeon_populator import Lair, OriginalInhabitants, UndergroundNatives, Explorers
from .dungeon_ager import DungeonAger
from encounters.encounter_api import EncounterSource
from treasure.treasure_api import HoardSource

example_events = [
    {   'type': 'populator',
        'style': 'original_inhabitants',
        'monster_set': ['haunted', 'necropolis']
    },
    {   'type': 'ager',
        'style': ['earthquake', 'age']
    },
    {   'type': 'populator',
        'style': 'underground_natives',
        'monster_set': ['caves', 'myconids', 'gricks', 'kobolds']
    },
    {   'type': 'ager',
        'style': ['flood', 'shadowfell', 'age']
    },
    {   'type': 'populator',
        'style': 'explorers',
        'monster_set': ['goblins', 'orcs', 'bugbears', 'bandits']
    }
]

populator_dict = {
        'explorers': Explorers,
        'underground_natives': UndergroundNatives,
        'lair': Lair,
        'original_inhabitants': OriginalInhabitants}

class Event:
    def __init__(self, event_details, encounter_level, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        if event_details['type'] == 'populator':
            encounter_source = EncounterSource(encounter_level=encounter_level,
                                               monster_sets=event_details['monster_sets'],
                                               random_state=self.random_state)
            treasure_source = HoardSource(encounter_level=encounter_level,
                                             random_state=self.random_state)
            populator = populator_dict[event_details['style']](encounter_source=encounter_source, treasure_source=treasure_source)
            self.effect = populator.populate
        elif event_details['type'] == 'ager':
            event_type = self.random_state.choice(event_details['style'])
            ager = DungeonAger(event_type,
                               random_state=self.random_state)
            self.effect = ager.age

class DungeonHistory:
    def __init__(self, events, encounter_level, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.events = [Event(event_details, encounter_level, random_state=self.random_state) for event_details in events]

    def alter_dungeon(self, layout):
        for event in self.events:
            event.effect(layout)
        return layout

