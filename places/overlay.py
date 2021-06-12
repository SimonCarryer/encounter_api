import random
import networkx as nx


class Overlay:
    def __init__(self, label, max_value, min_value):
        self.label = label
        self.max_value = max_value
        self.min_value = min_value

    def random_node(self, graph):
        return random.choice(list(graph.nodes()))

    def apply(self, graph):
        values = self.node_values(graph)
        for node, value in zip(graph.nodes, values):
            graph.nodes[node][self.label] = value
        for node, data in graph.nodes(data=True):
            for neighbour in data["neighbours"]:
                graph[node][neighbour][self.label] = graph.nodes[node]["height"] * \
                    graph.nodes[neighbour][self.label]


class HighPoint(Overlay):
    def node_values(self, graph):
        start = self.random_node(graph)
        distances = [nx.shortest_path_length(
            graph, start, node) for node in graph.nodes]
        values = [max([self.max_value-distance, self.min_value])
                  for distance in distances]
        return values


class LowPoint(Overlay):
    def node_values(self, graph):
        start = self.random_node(graph)
        distances = [nx.shortest_path_length(
            graph, start, node) for node in graph.nodes]
        values = [min([self.min_value+distance, self.max_value])
                  for distance in distances]
        return values


class TwoLow(Overlay):
    def node_values(self, graph):
        low1 = LowPoint(self.label, self.max_value, self.min_value)
        low2 = LowPoint(self.label, self.max_value, self.min_value)
        return [min([v1, v2]) for v1, v2 in zip(low1.node_values(graph), low2.node_values(graph))]


class TwoHigh(Overlay):
    def node_values(self, graph):
        low1 = HighPoint(self.label, self.max_value, self.min_value)
        low2 = HighPoint(self.label, self.max_value, self.min_value)
        return [max([v1, v2]) for v1, v2 in zip(low1.node_values(graph), low2.node_values(graph))]


class Scale(Overlay):
    def node_values(self, graph):
        values = [data[self.label] for node, data in graph.nodes(data=True)]
        top = max(values)
        bottom = min(values)
        old_scale = top - bottom
        new_scale = self.max_value - self.min_value
        return [int(round(((value - bottom) * new_scale)/old_scale + self.min_value, 0)) for value in values]
