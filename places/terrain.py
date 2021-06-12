import yaml
from .overlay import *

with open("data/terrain_features.yaml", "r") as f:
    features = yaml.load(f.read())


class Terrain:
    def __init__(self, terrain_type):
        self.type = terrain_type
        self.descriptions = features[terrain_type]["descriptions"]
        self.extras = features[terrain_type]["extra"]
        self.density = features[terrain_type]["density"]

    def choose_description(self, height, density):
        possible = [description
                    for description in self.descriptions if description["height"] == height and description.get("density", density) == density]
        return random.choice(possible)

    def choose_density(self, height, density):
        possible = [description
                    for description in self.density if description["density"] == density and description.get("height", height) == height]
        return random.choice(possible)

    def choose_extra(self, height, density):
        possible = [description["description"]
                    for description in self.extras if description.get("height", height) == height and description.get("density", density) == density]
        return random.choice(possible)

    def add_descriptions(self, graph):
        for node, data in graph.nodes(data=True):
            height = data["height"]
            density = data["density"]
            description = self.choose_description(height, density)
            data["description"].add(description["description"])
            if density in [1, 3] and description.get("density") is None:
                density_extra = self.choose_density(
                    height, density)["description"]
                data["description"].add(density_extra)
            if random.randint(1, 6) >= 5:
                extra = self.choose_extra(height, density)
                data["description"].add(extra)

    def apply(self, graph):
        # self.apply_overlays(graph)
        self.add_descriptions(graph)
        return graph
