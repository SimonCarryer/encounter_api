from .encounter_builder import EncounterBuilder
from .encounter_picker import EncounterPicker
from collections import Counter, defaultdict
from treasure.treasure_api import IndividualSource
import yaml
import random
from utils.library import monster_manual as monster_manual

with open('data/xp_values.yaml') as f:
    xp_values = yaml.load(f.read())

class EncounterSource:
    def __init__(self,
                xp_budget=None,
                encounter_level=None,
                character_level_dict=None,
                monster_sets=None,
                supplied_monster_manual=None,
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
        if supplied_monster_manual is None:
            self.monster_manual = monster_manual
        else:
            self.monster_manual = supplied_monster_manual
        if monster_sets is None:
            monster_set = self.random_state.choice(self.monster_manual.monster_set_names)
        else:
            monster_set = self.random_state.choice(monster_sets)
        self.monster_set = monster_set
        monsters = self.monster_manual.monsters(monster_set)
        encounters = EncounterBuilder(self.xp_budget, monsters, n_characters=self.n_characters).monster_lists
        self.encounter_picker = EncounterPicker(encounters, self.xp_budget, n_characters=self.n_characters, random_state=self.random_state)
        self.used_signs = set()
                
    def budget_from_character_dict(self, character_level_dict):
        xp_budget = 0
        for level in character_level_dict.keys():
            xp_budget += (xp_values[level]/4) * character_level_dict[level]
        return xp_budget

    def get_treasure(self, monsters):
        return IndividualSource(monsters, random_state=self.random_state).get_treasure()
        
    def get_encounter(self, difficulty=None, occurrence=None, style=None):
        encounter = self.encounter_picker.pick_encounter(difficulty=difficulty, occurrence=occurrence, style=style)
        response = {}
        if encounter['monsters'] == []:
            response['success'] = False
        else:
            response['success'] = True
            response['monster_set'] = self.monster_set
            response['monsters'] = [{'name': k, 'number': v} for k, v in dict(Counter([monster['Name'] for monster in encounter['monsters']])).items()]
            response['difficulty'] = encounter['difficulty']
            response['xp_value'] = int(encounter['xp_value'])
            response['monster_hash'] = encounter['monster_hash']
            response['treasure'] = self.get_treasure(encounter['monsters'])
        return response

    def get_sign(self):
        signs = [sign for sign in monster_manual.get_signs(self.monster_set) if sign not in self.used_signs]
        if len(signs) > 0:
            sign = self.random_state.choice(signs)
            self.used_signs.add(sign)
        else:
            sign = None
        return sign

