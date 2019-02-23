from .encounter import Encounter
from collections import Counter
from .monsters import MonsterManual
import yaml
import random

with open('data/xp_values.yaml') as f:
    xp_values = yaml.load(f.read())


class EncounterSource:
    def __init__(self,
                xp_budget=None,
                encounter_level=None,
                character_level_dict=None,
                monster_sets=None,
                monster_source=MonsterManual,
                style=None,
                random_state=None):
        if random_state is None:
            self.random_state = random.Random()
        else:
            self.random_state = random_state
        if xp_budget is not None:
            self.xp_budget = xp_budget
            self.n_characters = 4
        elif encounter_level is not None:
            self.xp_budget = xp_values[encounter_level]
            self.n_characters = 4
        elif character_level_dict is not None:
            self.xp_budget = self.budget_from_character_dict(character_level_dict)
            self.n_characters = sum([i for i in character_level_dict.values()])
        else:
            raise NoXPBudgetError
        self.monster_source = monster_source()
        if monster_sets is None:
            monster_set = self.random_state.choice(self.monster_source.monster_set_names)
        else:
            monster_set = self.random_state.choice(monster_sets)
        if monster_set == 'all':
            monster_set = None
        monsters = self.monster_source.monsters(monster_set, self.random_state)
        self.encounter = Encounter(self.xp_budget, monsters, random_state=self.random_state, style=style, n_characters=self.n_characters)
        
    def budget_from_character_dict(self, character_level_dict):
        xp_budget = 0
        for level in character_level_dict.keys():
            xp_budget += (xp_values[level]/4) * character_level_dict[level]
        return xp_budget
        
    def get_encounter(self):
        response = {}
        if self.encounter.monsters == []:
            response['success'] = False
        else:
            response['success'] = True
            response['monster_set'] = self.monster_source.name
            response['monsters'] = [{'name': k, 'number': v} for k, v in dict(Counter([monster['Name'] for monster in self.encounter.monsters])).items()]
            difficulty = self.encounter.adjusted_xp() / self.xp_budget
            if difficulty <= 0.8:
                response['difficulty'] = 'easy'
            elif difficulty > 1.2:
                response['difficulty'] = 'hard'
            else:
                response['difficulty'] = 'medium'
            response['xp_value'] = self.encounter.total_xp()
        return response