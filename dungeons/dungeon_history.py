from .dungeon_populator import Lair, OriginalInhabitants, UndergroundNatives, Explorers
from .dungeon_ager import DungeonAger
from encounters.encounter_api import EncounterSource
from treasure.treasure_api import HoardSource
from random import Random

populator_dict = {
        'explorers': Explorers,
        'underground_natives': UndergroundNatives,
        'lair': Lair,
        'original_inhabitants': OriginalInhabitants}
    
class Event:
    def __init__(self, event_details, encounter_level=None, random_state=None):
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
            ager = DungeonAger(cause=None, random_state=self.random_state)
            self.effect = ager.age

class DungeonHistory:
    def __init__(self, inhabitants, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.events = []
        self.create_events(inhabitants)

    def create_events(self, inhabitants):
        original_inhabitants = inhabitants.get('original_inhabitants')
        if original_inhabitants is not None:
            event_details = {
                'type': 'populator',
                'style': 'original_inhabitants',
                'monster_sets': [original_inhabitants]
            }
            event = Event(event_details, inhabitants['level'], random_state=self.random_state)
            self.events.append(event)
        if self.random_state.randint(1, 6) >= 4:
            event_details = {'type': 'ager'}
            event = Event(event_details, random_state=self.random_state)
            self.events.append(event)
        event_details = {
                'type': 'populator',
                'style': 'underground_natives',
                'monster_sets': ['caves', 'myconids', 'gricks']
            }
        event = Event(event_details, inhabitants['level'], random_state=self.random_state)
        self.events.append(event)
        if self.random_state.randint(1, 6) >= 4:
            event_details = {'type': 'ager'}
            event = Event(event_details, random_state=self.random_state)
            self.events.append(event)
        explorers = inhabitants.get('explorers')
        if explorers is not None:
            event_details = {
                'type': 'populator',
                'style': 'explorers',
                'monster_sets': [explorers]
            }
            event = Event(event_details, inhabitants['level'], random_state=self.random_state)
            self.events.append(event)


    def alter_dungeon(self, layout):
        for event in self.events:
            event.effect(layout)
        return layout

