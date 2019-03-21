import bisect
import yaml
import random
from .hoard import Hoard
from .individual import Individual

with open('data/xp_values.yaml') as f:
    xp_values = yaml.load(f.read())

class TreasureSource(object):
    def __init__(self,
                xp_budget=None,
                encounter_level=None,
                character_level_dict=None,
                random_state=None):
        if random_state is None:
            self.random_state = random.Random()
        else:
            self.random_state = random_state
        if encounter_level is not None:
            self.level = encounter_level
        elif xp_budget is not None:
            self.level = self.level_from_budget(xp_budget)
        elif character_level_dict is not None:
            xp_budget = self.budget_from_character_dict(character_level_dict)
            self.level = self.level_from_budget(xp_budget)

    def level_from_budget(self, xp_budget):
        idx = bisect.bisect_left(sorted(xp_values.values()), xp_budget)
        return sorted(list(xp_values.keys()))[idx]

    def budget_from_character_dict(self, character_level_dict):
        xp_budget = 0
        for level in character_level_dict.keys():
            xp_budget += (xp_values[level]/4) * character_level_dict[level]
        return xp_budget

class HoardSource(TreasureSource):
    def __init__(self,
                xp_budget=None,
                encounter_level=None,
                character_level_dict=None,
                random_state=None):
        TreasureSource.__init__(self,
                                xp_budget=xp_budget,
                                encounter_level=encounter_level,
                                character_level_dict=character_level_dict,
                                random_state=random_state)
        self.contents = Hoard(self.level, random_state=self.random_state)

    def get_treasure(self):
        response = {
            'objects': self.contents.objects,
            'items': self.contents.items,
            'coins': self.contents.coins
        }
        return response

class IndividualSource(TreasureSource):
    def __init__(self,
                xp_budget=None,
                encounter_level=None,
                character_level_dict=None,
                random_state=None):
        TreasureSource.__init__(self,
                                xp_budget=xp_budget,
                                encounter_level=encounter_level,
                                character_level_dict=character_level_dict,
                                random_state=random_state)
        self.contents = Individual(self.level, random_state=self.random_state)

    def get_treasure(self):
        response = {
            'coins': self.contents.coins
        }
        return response
