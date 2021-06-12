import networkx as nx
import random


class River:
    def __init__(self):
        pass

    def choose_path(self, graph):
        border_nodes = [node for node, data in graph.nodes(
            data=True) if data["borders_map_edge"]]
        start = random.choice(border_nodes)
        shortest_paths = nx.single_source_shortest_path(
            graph, start)
        paths = [shortest_paths[node] for node in border_nodes]
        path = sorted(paths, key=lambda x: len(x))[-1]
        return path

    def apply_topography(self, graph):
        river_nodes = [node for node, data in graph.nodes(
            data=True) if data.get("river") is not None]
        for node in graph.nodes():
            if node in river_nodes:
                graph.node[node]["height"] = 1
            else:
                shortest_paths = nx.single_target_shortest_path(
                    graph, node)
                height = min([len(shortest_paths[node])
                              for node in river_nodes])
                graph.node[node]["height"] = min([height, 3])

    def apply(self, graph):
        path = self.choose_path(graph)
        edges_in_path = list(zip(path, path[1:]))
        for idx, river_node in enumerate(path):
            graph.nodes[river_node]["river"] = idx
            if idx > 0:
                nodes = edges_in_path[idx-1]
                graph.nodes[river_node]["river_point"] = graph.edges[nodes]["midpoint"]
            else:
                graph.nodes[river_node]["river_point"] = [0, 0]
        self.apply_topography(graph)


class Road:
    def __init__(self):
        pass

    def choose_points(self, graph):
        target_height = min([data["height"] for node, data in graph.nodes(
            data=True) if data["borders_map_edge"]])
        possible_starts = [node for node, data in graph.nodes(
            data=True) if data["borders_map_edge"] and data["height"] == target_height]
        start = random.choice(possible_starts)
        possible_ends = [node for node in possible_starts if node !=
                         start and nx.shortest_path_length(graph, start, node) > 3]
        if len(possible_ends) > 0:
            end = random.choice(possible_ends)
        else:
            possible_ends = [node for node, data in graph.nodes(
                data=True) if data["borders_map_edge"] and node != start]
            end = random.choice(possible_ends)
        return start, end

    def choose_path(self, start, end, graph):
        path = nx.shortest_path(graph, start, end, weight="height")
        return path

    def apply(self, graph):
        start, end = self.choose_points(graph)
        path = self.choose_path(start, end, graph)
        edges_in_path = list(zip(path, path[1:]))
        for idx, road_node in enumerate(path):
            graph.nodes[road_node]["road"] = idx
            if idx > 0:
                nodes = edges_in_path[idx-1]
                graph.nodes[road_node]["road_point"] = graph.edges[nodes]["midpoint"]
            else:
                graph.nodes[road_node]["road_point"] = [0, 0]
