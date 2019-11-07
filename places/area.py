from random import Random
import yaml
from .place import Place
from npcs.npc import NPC
from monster_manual.monster_manual import MonsterManual

with open('data/terrain_features.yaml') as f:
    terrain_features = yaml.load(f)
    
with open('data/places.yaml') as f:
    places = yaml.load(f)
    
with open('data/history_features.yaml') as f:
    history_features = yaml.load(f)


class Area:
    def __init__(self, level, terrain, history, tags, random_state=None):
        self.level = level
        self.terrain = terrain
        self.history = history
        self.tags = history + [terrain] + tags
        self.other_features = {}
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        possible_features = terrain_features[terrain]
        for era in self.history:
            possible_features += history_features[era]
        self.features = self.random_state.sample(possible_features, 3)
        possible_places = [place for place in places if self.possible_place(place)]
        n = self.random_state.randint(2, 3)
        self.monster_manual = MonsterManual(terrain=self.terrain)
        self.places = [self.make_place(place) for place in self.random_state.sample(possible_places, n)]
        if self.random_state.randint(1, 6) >= 5:
            self.other_features['NPC'] = NPC(random_state=self.random_state).details()



    def make_place(self, place_type):
        return Place(place_type, self.level, self.monster_manual, random_state=self.random_state).details()

    def possible_place(self, place):
        return any([tag in places[place]['tags'] for tag in self.tags])

    def details(self):
        return {
            'places': self.places,
            'features': self.features,
            'terrain': self.terrain,
            'history': self.history,
            'other features': self.other_features
        }
