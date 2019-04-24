from random import Random
import networkx as nx

class DungeonLayout(nx.Graph):
    def __init__(self, n_rooms=0, connectivity_threshold=1.2, secret_chance=10, random_state=None):
        nx.Graph.__init__(self)
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.secret_chance = secret_chance
        self.tags = []
        self.history = []
        if n_rooms > 0:
            # make each room
            for room_idx in range(n_rooms):
                self.add_room(room_idx)
            # randomly add connections until connectivity threshold is reached
            while nx.average_node_connectivity(self) < connectivity_threshold:
                room1, room2 = self.random_state.sample(self.nodes(), 2)
                self.connect_rooms(room1, room2)
            # ensure all parts of the dungeon are reachable
            connected_components = [i for i in nx.connected_components(self)]
            if len(connected_components) > 1:
                for idx in range(len(connected_components)-1):
                    room = self.random_state.sample(connected_components[idx], 1)[0]
                    connecting_room = self.random_state.sample(connected_components[idx+1], 1)[0]
                    self.connect_rooms(room, connecting_room)
            # label nodes
            self.paths = {a: len(nx.shortest_path(self, 0, a)) for a in self.nodes()}
            self.tag_nodes()

    def add_room(self, room_idx):
        self.add_node(room_idx, tags=[], features=[])

    def connect_rooms(self, room, connecting_room):
        if self.random_state.randint(1, 10) >= self.secret_chance:
            weight = 3
            tags = ['secret']
            description = ''
        else:
            weight = 1
            tags = []
            description = ''
        self.add_edge(room, connecting_room, weight=weight, tags=tags, description=description)

    def tag_nodes(self):
        nodes = [(node, data) for node, data in self.nodes(data=True) if 'secret' not in data['tags']]
        central_nodes = [i for i in nx.articulation_points(self)]
        max_path = max(self.paths.values())
        for a, node in nodes:
            if a == 0:
                node['tags'].append('entrance')
            if a in central_nodes:
                node['tags'].append('central')
            if self.paths[a] == max_path:
                node['tags'].append('important')
            if len([i for i in self.neighbors(a)]) == 1 and a != 0:
                node['tags'].append('dead-end')
            if len([i for i in self.neighbors(a)]) >= 3:
                node['tags'].append('hub')
            node['distance'] = self.paths[a]
        self.label_secret_nodes()
    
    def label_secret_nodes(self):
        for node, data in self.nodes(data=True):
            if node > 0:
                data['distance'] = self.paths[node]
                paths = nx.all_simple_paths(self, 0, node)
                if all([self.any_secrets_in_path(path) for path in paths]):
                    data['tags'].append('secret')
        
    def any_secrets_in_path(self, path):
        for idx in range(len(path) -1):
            edge_data = self.get_edge_data(path[idx], path[idx+1])
            if 'secret' in edge_data['tags']:
                return True
        return False


