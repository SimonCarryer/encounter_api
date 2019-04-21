from random import Random
import yaml

with open('data/dungeon_types.yaml', 'r') as f:
    dungeon_rooms = {}
    dungeon_tags = {}
    dungeon_info = yaml.load(f)
    for purpose in dungeon_info.keys():
        rooms = []
        for idx, room in enumerate(dungeon_info[purpose]['rooms']):
            room['room_id'] = idx
            room['tags'] = room.get('tags', [])
            rooms.append(room)
        dungeon_rooms[purpose] = rooms
        dungeon_tags[purpose] = dungeon_info[purpose]['tags']


class DungeonFurnisher:
    def __init__(self, purpose, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.purpose = purpose
        self.room_type_list = dungeon_rooms[purpose]
        self.used_room_types = []

    def furnish(self, layout):
        for n, room in layout.nodes(data=True):
            room['description'] = self.choose_room_type(room['tags'])
        layout.purpose = self.purpose
        return layout

    def appropriate_room_type(self, room_type, room_tags):
        appropriate = False
        if room_tags == [] and 'secret' not in room_type['tags'] and 'important' not in room_type['tags']:
            appropriate = True
        elif any([tag in room_type['tags'] for tag in room_tags]):
            appropriate = True
        return appropriate

    def choose_room_type(self, room_tags):
        suitable_room_types = [room_type for room_type in self.room_type_list if self.appropriate_room_type(room_type, room_tags)]
        final = [room_type for room_type in suitable_room_types if room_type['room_id'] not in self.used_room_types]
        if len(final) > 0:
            room_type = self.random_state.choice(final)
        elif len(suitable_room_types) > 0:
            room_type = self.random_state.choice(suitable_room_types)
        else:
            room_type = self.random_state.choice(self.room_type_list)
        self.used_room_types.append(room['room_id'])
        return room_type['description']