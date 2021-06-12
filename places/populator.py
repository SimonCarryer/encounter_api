from monster_manual.monster_manual import MonsterManual
from encounters.encounter_api import EncounterSource
import random


class PlacePopulator:
    def __init__(self, terrain=None, all_tags=None, none_tags=None, any_tags=None, level=None, monster_set=None):
        self.mm = MonsterManual(terrain=terrain)
        if monster_set is None:
            sets = self.mm.get_monster_sets(
                all_tags=all_tags, none_tags=none_tags, any_tags=any_tags, level=level)
            monster_set = random.choice(sets)
        self.monster_set = monster_set
        self.source = EncounterSource(
            encounter_level=level, monster_sets=[self.monster_set])

    def apply(self, graph):
        for node, data in graph.nodes(data=True):
            if random.randint(1, 6) >= 5:
                data["signs"] = self.source.get_sign()
                data["encounter"] = self.source.get_encounter()


class Creatures(PlacePopulator):
    def apply(self, graph):
        for node, data in graph.nodes(data=True):
            if random.randint(1, 6) + data["height"] >= 7 and data.get("road") is None:
                data["signs"] = self.source.get_sign()
                data["encounter"] = self.source.get_encounter()
