import bisect
from collections import defaultdict
from copy import deepcopy
from .xp_calculator import XPCalulator

big_adjustments = {k: v for k, v in [(0, 0.5), (1, 0.5), (2, 1), (3, 1.5), (4, 1.5), (5, 1.5), (6, 1.5), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2.5), (12, 2.5), (13, 2.5), (14, 2.5), (15, 3), (16, 3), (17, 3), (18, 3), (19, 3), (20, 3)]}
med_adjustments = {k: v for k, v in [(0, 1), (1, 1), (2, 1.5), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2.5), (8, 2.5), (9, 2.5), (10, 2.5), (11, 3), (12, 3), (13, 3), (14, 3), (15, 4), (16, 4), (17, 4), (18, 4), (19, 4), (20, 4)]}
small_adjustments = {k: v for k, v in [(0, 1.5), (1, 1.5), (2, 2), (3, 2.5), (4, 2.5), (5, 2.5), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 4), (12, 4), (13, 4), (14, 4), (15, 5), (16, 5), (17, 5), (18, 5), (19, 5), (20, 5)]}


class EncounterBuilder:
    def __init__(self,
                 xp_budget,
                 monster_source,
                 lower_bound=0.5,
                 upper_bound=1.5,
                 n_characters=4):
        self.xp_calculator = XPCalulator(n_characters=n_characters)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.xp_budget = xp_budget
        self.monster_source = monster_source
        self.max_n_monsters = 10
        for idx, monster in enumerate(self.monster_source):
            monster['idx'] = idx
        self.monster_lookup = {monster['Name']: monster for monster in monster_source}
        self.monster_lists = []
        self.pick_monsters([])
        counter = 0
        while len(self.monster_lists) == 0 and counter <= 3:
            counter += 1
            self.lower_bound -= 0.1
            self.upper_bound += 0.1
            self.pick_monsters([])

    def right_role(self, existing_monster_list):
        possible_monsters = self.monster_source
        current_roles = [monster['role'] for monster in existing_monster_list]
        current_names = [monster['Name'] for monster in existing_monster_list]
        if len(set(current_names)) >= 3:
            possible_monsters = [monster for monster in possible_monsters if monster['Name'] in current_names]
        if 'leader' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'leader']
        if 'elite' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'elite' or monster['Name'] in current_names]
        if 'troops' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'troops' or monster['Name'] in current_names]
        if 'natural hazard' not in current_roles and current_roles != []:
            possible_monsters = [monster for monster in possible_monsters if monster['Name'] in current_names or monster['role'] != 'natural hazard']
        if 'natural hazard' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['Name'] in current_names or monster['role'] == 'environmental hazard']
        if 'pet' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'pet' or monster['Name'] in current_names]
        if 'solo' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] == 'environmental hazard']
        if 'solo' not in current_roles and len(current_roles) > 0:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'solo']
        if 'environmental hazard' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'environmental hazard']
        return possible_monsters

    def right_index_monsters(self, existing_monster_list):
        if len(existing_monster_list) == 0:
            max_idx = 0
        else:
            max_idx = max([monster['idx'] for monster in existing_monster_list])
        possible_monsters = [monster for monster in self.monster_source if monster['idx'] >= max_idx]
        return possible_monsters

    def possible_monsters(self, existing_monster_list):
        right_index = self.right_index_monsters(existing_monster_list)
        right_roles = self.right_role(existing_monster_list)
        return [monster for monster in right_index if monster in right_roles]
        
    def pick_monsters(self, monsters):
        current_total = self.xp_calculator.adjusted_xp_sum(monsters)
        if len(monsters) >= self.max_n_monsters:
            return None
        if current_total > self.xp_budget * self.upper_bound:
            return None
        possible_monsters = self.possible_monsters(monsters)
        if len(possible_monsters) > 0:
            for monster in possible_monsters:
                self.pick_monsters([monster] + monsters)
        if current_total > self.xp_budget * self.lower_bound:
            self.monster_lists.append(monsters)
