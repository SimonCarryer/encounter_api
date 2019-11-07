import yaml
from random import Random
from monster_manual.monster_manual import MonsterManual
from encounters.wandering_monsters import WanderingMonsters
from encounters.encounter_api import EncounterSource

with open('data/places.yaml') as f:
    places = yaml.load(f)

class Place:
    def __init__(self, place_type, level, monster_manual, random_state=None):
        self.place_type = place_type
        self.monster_manual = monster_manual
        self.level = level
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.locations = []
        n = self.random_state.randint(2, 3)
        for location in self.random_state.sample(places[self.place_type]['locations'], n):
            self.locations.append(location)

    def encounters(self):
        tags = places[self.place_type]['encounters']
        monster_sets = self.monster_manual.get_monster_sets(any_tags=tags.get('any'), none_tags=tags.get('none'))
        monster_set = self.random_state.choice(monster_sets)
        return {
            'random encounters': WanderingMonsters(self.level, [monster_set], random_state=self.random_state).build_table(),
            'boss': EncounterSource(encounter_level=self.level, monster_sets=[monster_set], random_state=self.random_state).get_encounter(difficulty='hard', style='leader')
        }

    def details(self):
        return {
            'type': self.place_type,
            'locations': self.locations,
            'encounters': self.encounters()
        }