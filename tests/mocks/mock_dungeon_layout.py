import networkx as nx

class MockDungeonLayout(nx.Graph):
    def __init__(self):
        nx.Graph.__init__(self)
        for idx, tags in enumerate([['entrance'], ['dead-end'], ['central'], [], ['secret', 'trap'], ['important'], []]):
            self.add_node(idx, tags=tags, features=[], distance=idx)
        for start, end, weight in [(0, 1, 1), (1, 2, 3), (1, 3, 1), (3, 4, 4), (4, 5, 1), (3, 6, 1)]:
            self.add_edge(start, end, weight=weight)
        self.tags = []
        self.purpose = 'temple'
        self.events = []