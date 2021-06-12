import networkx as nx
import numpy as np
from .map_builder import RegionMapBuilder


class VoronoiMap(nx.Graph):
    def build(self, map_regions):
        for region in map_regions["regions"]:
            node = region["region_id"]
            self.add_node(node,
                          region_id=region["region_id"],
                          pos=region["centroid"].tolist(),
                          boundaries=region["boundaries"].tolist(),
                          point=region["point"].tolist(),
                          random_point=region["random_point"],
                          borders_map_edge=region["borders_map_edge"],
                          density=region["area"],
                          neighbours=region["neighbours"],
                          description=HexDescription()
                          )
            for neighbour in region["neighbours"]:
                midpoint = map_regions["midpoints"].get(
                    tuple(sorted((node, neighbour))))
                self.add_edge(node, neighbour, midpoint=midpoint)
        return self


class HexMap:
    def __init__(self, n_regions):
        self.map_regions = RegionMapBuilder(
            centralise_points=False, relax=0).build(n_regions)
        self.G = VoronoiMap().build(self.map_regions)

    def layout(self):
        for node in self.G:
            self.G.nodes[node]["description"] = self.G.nodes[node]["description"].render()
        hexes = sorted([data for node, data in self.G.nodes(
            data=True)], key=lambda x: x["region_id"])
        edges = self.map_regions["ridges"]
        return {
            "hexes": hexes,
            "edges": edges
        }


class HexDescription:
    def __init__(self):
        self.paragraphs = [[]]

    def add(self, sentence, new_paragraph=False):
        if new_paragraph:
            self.paragraphs.append([])
        self.paragraphs[-1].append(sentence)

    def render(self):
        return [". ".join(sentences) + "." for sentences in self.paragraphs]


class HexLocations:
    def __init__(self):
        pass
