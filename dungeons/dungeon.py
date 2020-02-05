from random import Random
import networkx as nx

letters = 'abcdefghijklmnopqrstuvwxyz'

class Dungeon:
    def __init__(self,
                 layout,
                 random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.layout = layout
        self.room_ids = self.get_room_ids()


    def get_room_ids(self):
        '''get the name of the room by distance from the entrance, so the module is easy to read.'''
        distances = [(data['distance'], idx) for idx, (node, data) in enumerate(self.layout.nodes(data=True))]
        return {room_idx: room_id+1 for room_id, (distance, room_idx) in enumerate(sorted(distances, key=lambda x: x[0]))}

    def get_room_passages(self, room_idx):
        passages = self.layout.edges(room_idx, data=True)
        adjoining_passages = [data for a, b, data in passages if min(self.room_ids[a], self.room_ids[b]) == self.room_ids[room_idx] and data['description'] != '']
        for idx, data in enumerate(adjoining_passages):
            data['letter'] = str(self.room_ids[room_idx]) + letters[idx]
        return [{'letter': data['letter'], 'description': data['description']} for data in adjoining_passages]


    def module(self):
        module = {'rooms':[],
                  'passages': []}
        rooms = []
        for room_idx, data in self.layout.nodes(data=True):
            room = data
            room['room_id'] = self.room_ids[room_idx]
            room['adjoining_passages'] = self.get_room_passages(room_idx)
            if room.get('sign') is not None:
                room['sign'] = str(room.get('sign'))
            rooms.append(room)
        module['rooms'] = sorted(rooms, key=lambda x: x['room_id'])
        seq = 0
        for start, end, data in self.layout.edges(data=True):
            if data['description'] != '':
                passage = {'description': data.get('description', '')}
                seq += 1
                module['passages'].append(passage)
        module['map'] = self.map()
        module['dungeon_type'] = self.layout.purpose
        module['dungeon_terrain'] = self.layout.terrain
        module['history'] = self.layout.events
        module['wandering_monster_table'] = self.layout.wandering_monster_table
        module['name'] = self.layout.name
        module['level'] = self.layout.level
        return module

    def make_postions(self, arr, max_dim=300):
        min_ = min(arr)
        translate = -min_
        arr = [v + translate for v in arr]
        max_ = max(arr)
        scale = max_dim/max_
        return [int(val * scale) for val in arr]

    def map(self):
        pos = nx.spring_layout(self.layout, fixed=[0], pos={0: (0, 1)}, weight=None, seed=self.random_state.randint(1, 256))
        xs = self.make_postions([r[0] for r in pos.values()])
        ys = self.make_postions([r[1] for r in pos.values()])
        room_ids = self.get_room_ids()
        rooms = []
        for room_idx, (x, y) in enumerate(zip(xs, ys)):
            room = {
                'room_id': room_ids[room_idx],
                'x': x,
                'y': y,
                'h': 40 + self.random_state.randint(0, 30),
                'w': 40 + self.random_state.randint(0, 40),
                'entrance': True if 'entrance' in self.layout.node[room_idx]['tags'] else False, # yeah I know.
                'uninhabitable': True if 'uninhabitable' in self.layout.node[room_idx]['tags'] else False
            }
            rooms.append(room)
        passages = []
        seq = 0
        for start, end, data in self.layout.edges(data=True):
            passage = {
                'secret': 'secret' in data.get('tags', []),
                'x1': xs[start] +20,
                'y1': ys[start] +20,
                'x2': xs[end] +20,
                'y2': ys[end] +20,
                'label': data.get('letter') if data['description'] != '' else None,
                'label_x': int((xs[start] + xs[end])/2) + 20,
                'label_y': int((ys[start] + ys[end])/2)
                }
            passages.append(passage)
            if data['description'] != '':
                seq += 1
        return {'rooms': rooms, 'passages': passages}






