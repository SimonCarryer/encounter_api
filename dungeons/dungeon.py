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

    def module(self):
        module = {'rooms':[],
                  'passages': []}
        for room_id, data in self.layout.nodes(data=True):
            room = data
            room['room_id'] = room_id+1
            module['rooms'].append(room)
        seq = 0
        for start, end, data in self.layout.edges(data=True):
            if data['weight'] >=2:
                passage = {'description': data['description']}
                passage['letter'] = letters[seq]
                seq += 1
                module['passages'].append(passage)
        module['map'] = self.map()
        module['dungeon_type'] = self.layout.purpose
        return module

    def make_postions(self, arr, max_dim=300):
        min_ = min(arr)
        translate = -min_
        arr = [v + translate for v in arr]
        max_ = max(arr)
        scale = max_dim/max_
        return [int(val * scale) for val in arr]
        

    def map(self):
        pos = nx.spring_layout(self.layout, fixed=[0], pos={0: (0, 1)})
        xs = self.make_postions([r[0] for r in pos.values()])
        ys = self.make_postions([r[1] for r in pos.values()])
        rooms = []
        for room_id, (x, y) in enumerate(zip(xs, ys)):
            room = {
                'room_id': room_id+1,
                'x': x,
                'y': y,
                'h': 40,
                'w': 40,
                'entrance': True if 'entrance' in self.layout.node[room_id]['tags'] else False
            }
            rooms.append(room)
        passages = []
        seq = 0
        for start, end, data in self.layout.edges(data=True):
            passage = {
                'style': 'solid' if data['weight'] < 3 else 'dashed',
                'x1': xs[start] +20,
                'y1': ys[start] +20,
                'x2': xs[end] +20,
                'y2': ys[end] +20,
                'label': letters[seq]+'.' if data['weight'] >= 2 else None,
                'label_x': int((xs[start] + xs[end])/2) + 30,
                'label_y': int((ys[start] + ys[end])/2)
                }
            passages.append(passage)
            if data['weight'] >= 2:
                seq += 1
        return {'rooms': rooms, 'passages': passages}






