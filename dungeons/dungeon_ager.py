from random import Random
import yaml

with open('data/dungeon_age.yaml', 'r') as f:
    dungeon_age = yaml.load(f)
    for cause in dungeon_age.keys():
        for idx, room_effect in enumerate(dungeon_age[cause]['rooms']):
            room_effect['id'] = idx
            room_effect['tags'] = room_effect.get('tags', [])
        for idx, passage_effect in enumerate(dungeon_age[cause]['passages']):
            passage_effect['id'] = idx

class DungeonAger:
    def __init__(self, cause, random_state=None, age_chance=5):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.age_chance = age_chance
        self.room_effects = dungeon_age[cause]['rooms']
        self.passage_effects = dungeon_age[cause]['passages']
        self.used_room_effects = []
        self.used_passage_effects = []

    def age(self, layout):
        for node, data in layout.nodes(data=True):
            if self.random_state.randint(1, 6) >= self.age_chance:
                effects = [effect for effect in self.room_effects if effect['id'] not in self.used_room_effects]
                if len(effects) > 0:
                    age_effect = self.random_state.choice(effects)
                    data['tags'] += age_effect['tags']
                    current_description = data.get('description', '')
                    data['description'] = ' '.join([current_description, age_effect['description']])
                    self.used_room_effects.append(age_effect['id'])
        for start, end, data in layout.edges(data=True):
            if self.random_state.randint(1, 6) >= self.age_chance:
                effects = [effect for effect in self.passage_effects if effect['id'] not in self.used_passage_effects]
                if len(effects) > 0:
                    age_effect = self.random_state.choice(effects)
                    data['weight'] = age_effect['weight']
                    current_description = data.get('description', '')
                    data['description'] = ' '.join([current_description, age_effect['description']])
                    self.used_passage_effects.append(age_effect['id'])
        return layout
