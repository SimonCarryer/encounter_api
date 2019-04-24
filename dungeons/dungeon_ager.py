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
            passage_effect['description'] = passage_effect.get('description', '')

class DungeonAger:
    def __init__(self, cause=None, random_state=None, required_tags=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        if cause is None:
            self.cause = self.random_state.choice(list(dungeon_age.keys()))
        else:
            self.cause = cause
        self.room_effects = dungeon_age[self.cause]['rooms']
        self.passage_effects = dungeon_age[self.cause]['passages']
        self.tags = dungeon_age[self.cause]['tags']
        self.used_room_effects = []
        self.used_passage_effects = []

    def choose_room_effects(self, layout):
        rooms = layout.nodes()
        effects_min = int(len(rooms)*0.33)
        effects_max =int(len(rooms)*0.66)
        n_effects = min([self.random_state.randint(effects_min, effects_max), len(self.room_effects)])
        affected_rooms = self.random_state.sample(rooms, n_effects)
        effects = self.random_state.sample(self.room_effects, n_effects)
        for effect, room in zip(effects, affected_rooms):
            layout.node[room]['tags'] += effect['tags']
            if self.tags is not None:
                layout.node[room]['tags'] += self.tags
            current_description = layout.node[room].get('description', '')
            layout.node[room]['description'] = ' '.join([current_description, effect['description']])

    def choose_passage_effects(self, layout):
        passages = layout.edges()
        effects_min = int(len(passages)*0.33)
        effects_max =int(len(passages)*0.66)
        n_effects = min([self.random_state.randint(effects_min, effects_max), len(self.passage_effects)])
        affected_passages = self.random_state.sample(passages, n_effects)
        effects = self.random_state.sample(self.passage_effects, n_effects)
        for effect, passage in zip(effects, affected_passages):
            layout[passage[0]][passage[1]]['weight'] = max([effect['weight'], layout[passage[0]][passage[1]]['weight']])
            current_description = layout[passage[0]][passage[1]].get('description', '')
            layout[passage[0]][passage[1]]['description'] = ' '.join([current_description, effect['description']])

    def add_event(self, layout):
        event = 'Event: %s' % self.cause
        layout.history.append(event)

    def age(self, layout):
        self.choose_room_effects(layout)
        self.choose_passage_effects(layout)
        self.add_event(layout)
        return layout
