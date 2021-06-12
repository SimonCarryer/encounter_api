import yaml
import random
from .hexmap import HexMap
from .terrain import Terrain
from .river import River, Road
from .overlay import *
from .populator import Creatures


class PlaceSource():
    def __init__(self):
        pass

    def get_place(self):
        place_type = random.choice([RiverValley, ForestHills])
        n_regions = random.randint(15, 19)
        return place_type(n_regions).layout()


class Place:
    def __init__(self, n_regions):
        self.hexmap = HexMap(n_regions)
        self.hexes = self.hexmap.G
        self.apply()

    def layout(self):
        return self.hexmap.layout()


class RiverValley(Place):
    def apply(self):
        river = River()
        river.apply(self.hexes)
        terrain = Terrain("forest")
        terrain.apply(self.hexes)
        encounters = Creatures(
            terrain="forest", monster_set="forest", level=1)
        encounters.apply(self.hexes)


class ForestHills(Place):
    def apply(self):
        overlay = TwoHigh("height", 3, 1)
        overlay.apply(self.hexes)
        if random.randint(1, 6) >= 5:
            road = Road()
            road.apply(self.hexes)
        terrain = Terrain("forest")
        terrain.apply(self.hexes)
        encounters = Creatures(
            terrain="forest", monster_set="forest", level=1)
        encounters.apply(self.hexes)
