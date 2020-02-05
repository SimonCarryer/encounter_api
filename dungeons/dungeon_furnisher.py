from random import Random
from traps.trap_api import TrapSource
from string import Template
from names.name_api import NameGenerator
import yaml

with open('data/dungeon_types.yaml', 'r') as f:
    dungeon_rooms = {}
    dungeon_tags = {}
    secret_passages = {}
    extra_details = {}
    dungeon_info = yaml.load(f)
    for purpose in dungeon_info.keys():
        rooms = []
        for idx, room in enumerate(dungeon_info[purpose]['rooms']):
            room['room_id'] = idx
            room['tags'] = room.get('tags', [])
            rooms.append(room)
        dungeon_rooms[purpose] = rooms
        secret_passages[purpose] = dungeon_info[purpose]['secret passages']
        extra_details[purpose] = dungeon_info[purpose]['extra details']

with open('data/special_furnishings.yaml', 'r') as f:
    special_furnishings_data = yaml.load(f)

class DungeonFurnisher:
    def __init__(self, purpose, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.purpose = purpose
        self.room_type_list = dungeon_rooms[purpose]
        self.used_room_types = []
        self.special_furnishings = [f(random_state=self.random_state) for f in [Fountain, Sarcophagus, Portal, Statue, MagicCrystal, Bones]]

    def furnish(self, layout):
        for n, room in layout.nodes(data=True):
            room_type = self.choose_room_type(room['tags'])
            room['description'] = room_type['description']
            if self.random_state.randint(1, 6) >= 5:
                extra = self.random_state.choice(extra_details[self.purpose])
                room['description'] += ' ' + extra
            room['tags'] += room_type['tags']
        for start, end, data in layout.edges(data=True):
            if 'secret' in data.get('tags', []):
                data['description'] = self.random_state.choice(secret_passages[self.purpose])
        layout.purpose = self.purpose
        if self.random_state.randint(1, 6) >= 5:
            self.get_special_furnishings(layout)
        return layout

    def get_special_furnishings(self, layout):
        possible_choices = [furnishing for furnishing in self.special_furnishings if furnishing.appropriate(layout)]
        if len(possible_choices) > 0:
            special_furnishing = self.random_state.choice(possible_choices)
            special_furnishing.add_special_furnishing(layout)

    def appropriate_room_type(self, room_type, room_tags):
        appropriate = False
        if room_tags == [] and 'secret' not in room_type['tags'] and 'important' not in room_type['tags'] and 'entrance' not in room_type['tags']:
            appropriate = True
        elif 'secret' in room_tags and 'secret' not in room_type['tags']:
            appropriate = False
        elif any([tag in room_type['tags'] for tag in room_tags]):
            appropriate = True
        if 'entrance' in room_type['tags'] and 'entrance' not in room_tags:
            appropriate = False
        return appropriate

    def suitable_rooms(self, room_tags):
        return [room_type for room_type in self.room_type_list if self.appropriate_room_type(room_type, room_tags)]

    def choose_room_type(self, room_tags):
        suitable_room_types = self.suitable_rooms(room_tags)
        final = [room_type for room_type in suitable_room_types if room_type['room_id'] not in self.used_room_types]
        if len(final) > 0:
            room_type = self.random_state.choice(final)
        elif len(suitable_room_types) > 0:
            room_type = self.random_state.choice(suitable_room_types)
        else:
            room_type = self.random_state.choice(self.room_type_list)
        self.used_room_types.append(room_type['room_id'])
        return room_type

class SpecialFurnishing:
    def __init__(self, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state

    def appropriate(self, layout):
        return True

    def best_room(self, layout):
        max_dist = max([data['distance'] for node, data in layout.nodes(data=True)])
        possible_rooms = [node for node, data in layout.nodes(data=True) if data['distance'] == max_dist]
        return self.random_state.choice(possible_rooms)

    def add_special_furnishing(self, layout):
        room = self.best_room(layout)
        layout.node[room]['description'] += self.get_description()

class Fountain(SpecialFurnishing):
    def get_description(self):
        template = Template(self.random_state.choice(special_furnishings_data['fountain']['templates']))
        creature = self.random_state.choice(special_furnishings_data['fountain']['creatures'])
        effect_template = Template(self.random_state.choice(special_furnishings_data['fountain']['effects']))
        verb = self.random_state.choice(special_furnishings_data['fountain']['verbs'])
        potion = self.random_state.choice(special_furnishings_data['fountain']['potions'])
        disclaimer = 'Characters can benefit from any positive effects only once per long rest, and the water ceases to function away from the fountain.'
        description = template.substitute({'creature': creature})
        effect = effect_template.substitute({'verb': verb, 'potion': potion, 'disclaimer': disclaimer})
        return ' '.join(['', description, effect])

    def appropriate(self, layout):
        return layout.purpose != 'mine'

class Sarcophagus(SpecialFurnishing):
    def appropriate(self, layout):
        return layout.purpose == 'tomb'

    def get_description(self):
        base = ' In this room there is '
        template = self.random_state.choice(special_furnishings_data['sarcophagus']['templates'])
        effect = self.random_state.choice(special_furnishings_data['sarcophagus']['effects'])
        d = {}
        for word in ['noun', 'material', 'adjective', 'spell', 'motif']:
            d[word] = self.random_state.choice(special_furnishings_data['sarcophagus'][word+'s'])
        return Template(' '.join([base, template, effect])).substitute(d)

class Portal(SpecialFurnishing):
    def appropriate(self, layout):
        return layout.purpose in ['temple', 'treasure vault', 'stronghold']

    def get_description(self):
        base = ''
        template = self.random_state.choice(special_furnishings_data['portal']['templates'])
        effect = self.random_state.choice(special_furnishings_data['portal']['effects'])
        d = {}
        for word in ['shape', 'material', 'motif', 'spell', 'activation']:
            d[word] = self.random_state.choice(special_furnishings_data['portal'][word+'s'])
        return Template(' '.join([base, template, effect])).substitute(d)

class Statue(SpecialFurnishing):
    def appropriate(self, layout):
        return layout.purpose in ['temple', 'treasure vault', 'stronghold']

    def get_description(self):
        base = ' This room contains'
        motif, other_motif = self.random_state.sample(special_furnishings_data['statue']['motif'], 2)
        fancy_name = NameGenerator().fancy_name()
        template = self.random_state.choice(special_furnishings_data['statue']['templates'])
        enticement = self.random_state.choice(special_furnishings_data['statue']['enticements'])
        effect = self.random_state.choice(special_furnishings_data['statue']['effects'])
        d = {'motif': motif, 'other_motif': other_motif, 'fancy_name': fancy_name}
        for word in ['single_activity', 'material', 'pair_activity', 'penalty']:
            d[word] = self.random_state.choice(special_furnishings_data['statue'][word])
        return Template(' '.join([base, template, enticement, effect])).substitute(d)

class MagicCrystal(SpecialFurnishing):
    def appropriate(self, layout):
        return layout.purpose in ['mine', 'cave']

    def get_description(self):
        template = self.random_state.choice(special_furnishings_data['magic crystal']['templates'])
        effect = self.random_state.choice(special_furnishings_data['magic crystal']['effects'])
        admonishment = self.random_state.choice(special_furnishings_data['magic crystal']['admonishments'])
        d = {}
        for word in ['noun', 'colour', 'verb', 'spell']:
            d[word] = self.random_state.choice(special_furnishings_data['magic crystal'][word+'s'])
        return ' ' + Template(' '.join([template, effect, admonishment])).substitute(d)

class Bones(SpecialFurnishing):
    def appropriate(self, layout):
        return layout.purpose in ['mine', 'cave']

    def get_description(self):
        template = self.random_state.choice(special_furnishings_data['bones']['template'])
        condition = self.random_state.choice(special_furnishings_data['bones']['condition'])
        effect = self.random_state.choice(special_furnishings_data['bones']['effect'])
        trigger = self.random_state.choice(special_furnishings_data['bones']['trigger'])
        choices = [
            [template, condition, trigger, effect],
            [template, condition],
            [template, trigger, effect]
        ]
        parts = ' '.join(self.random_state.choice(choices))
        template = Template(parts)
        d = {i: self.random_state.choice(special_furnishings_data['bones'][i]) for i in ['creature', 'material']}
        return ' '+template.substitute(d)