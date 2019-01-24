import bisect
from collections import defaultdict
from copy import deepcopy
from random import Random

adjustments = [(1, 1), (2, 1.5), (6, 2), (10, 2.5), (14, 3), (1000, 4)]

'''
Leader: Only ever one leader in an encounter
TODO: Pet: Never encountered alone
Elite: Never more than one kind of elite in an encounter
Troops: Never more than one kind of troops in an encounter
Natural Hazard: Only found with their own kind
Solo: Only encountered alone
Environmental Hazard: Shows up alongside other kinds
Rare: 10% of encounters should have a rare monster
Uncommon: 30% of encounters should have an uncommon monster

Styles:
Leader: Always has a leader
Elite: Always has an elite
Basic: No leaders or elites
'''

class Encounter:
    def __init__(self, xp_budget, monster_source, random_state=None, respect_roles=True, occurrence=None, style=None, lower_bound=0.5, upper_bound=1.5):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.xp_budget = xp_budget
        self.monster_source = monster_source
        for idx, monster in enumerate(self.monster_source):
            monster['idx'] = idx
        self.monster_lookup = {monster['Name']: monster for monster in monster_source}
        self.monster_lists = []
        self.monsters = []
        self.xp_value = 0
        if occurrence is None:
            roll = self.random_state.randint(1,11)
            if roll <= 6:
                self.occurrence = 'common'
            elif roll <= 9:
                self.occurrence = 'uncommon'
            else:
                self.occurrence = 'rare'
        else:
            self.occurrence = occurrence
        self.style = style
        if self.style == 'basic':
            self.monster_source = [monster for monster in self.monster_source if monster['role'] not in ['leader', 'elite']]
        if self.style == 'elite':
            self.monster_source = [monster for monster in self.monster_source if monster['role'] not in ['leader']]
        self.pick_monsters([])
        self.choose_monster_list()
        
    def choose_monster_list(self):
        correct_occurrence_lists = self.get_lists_of_correct_occurrence()
        all_lists = self.monster_lists
        right_occurrence_monsters = set()
        all_monsters = set()
        for l in correct_occurrence_lists:
            for m in l:
                if m['role'] == self.style or self.style not in ['leader', 'elite']:
                    right_occurrence_monsters.add(m['Name'])
        for l in all_lists:
            for m in l:
                if m['role'] == self.style or self.style not in ['leader', 'elite']:
                    all_monsters.add(m['Name'])
        all_monsters = sorted(list(all_monsters))
        right_occurrence_monsters = sorted(list(right_occurrence_monsters))
        monster_list = []
        if len(right_occurrence_monsters) > 0:
            lists = correct_occurrence_lists
            right_monsters = right_occurrence_monsters
        else:
            lists = all_lists
            right_monsters = all_monsters
        if len(right_monsters) > 0:
            monster = self.random_state.choice(right_monsters)
            right_lists = [l for l in lists if monster in [m['Name'] for m in l]]
            if len(right_lists) > 0:
                monster_list = self.random_state.choice(right_lists)
        self.monsters = monster_list

    def adjust_xp_for_monster_counts(self, monster_xp, adjust=1):
        monster_count = len(self.monsters) + adjust
        adjustment = self.calculate_adjustment(monster_count)
        return adjustment * monster_xp

    def calculate_adjustment(self, n_monsters):
        return adjustments[bisect.bisect_left([i[0] for i in adjustments], n_monsters)][1]

    def adjusted_xp_sum(self, monster_list, adjust=1):
        monster_count = len(monster_list) + adjust
        adjustment = self.calculate_adjustment(monster_count)
        return sum([monster['XP'] * adjustment for monster in monster_list])

    def right_challenge_monsters(self, existing_monster_list):
        if len(existing_monster_list) > 0:
            current_average = sum([m['XP'] for m in existing_monster_list])/len(existing_monster_list)
        else:
            current_average = 0
        threshold = max([current_average * 0.1, self.xp_budget * 0.05])
        return [monster for monster in self.monster_source if monster['role'] == 'troops' or monster['XP'] >= threshold]

    def right_role(self, existing_monster_list):
        possible_monsters = self.monster_source
        current_roles = [monster['role'] for monster in existing_monster_list]
        current_names = [monster['Name'] for monster in existing_monster_list]
        if 'leader' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'leader']
        if 'elite' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'elite' or monster['Name'] in current_names]
        if 'troops' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'troops' or monster['Name'] in current_names]
        # if existing_monster_list == []:
        #     possible_monsters = [monster for monster in possible_monsters if monster['role'] not in ['pet', 'environmental hazard']]
        if 'natural hazard' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['Name'] in current_names or monster['role'] == 'environmental hazard']
        if 'pet' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] != 'pet' or monster['Name'] in current_names]
        if 'solo' in current_roles:
            possible_monsters = [monster for monster in possible_monsters if monster['role'] == 'environmental hazard']
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
        right_challenge = self.right_challenge_monsters(existing_monster_list)
        right_roles = self.right_role(existing_monster_list)
        return [monster for monster in right_index if monster in right_roles]
        
    def pick_monsters(self, monsters):
        current_total = self.adjusted_xp_sum(monsters, adjust=0)
        if len(monsters) > 18:
            return None
        if current_total > self.xp_budget * self.upper_bound:
            return None
        possible_monsters = self.possible_monsters(monsters)
        if len(possible_monsters) > 0:
            for monster in possible_monsters:
                self.pick_monsters([monster] + monsters)
        if current_total > self.xp_budget * self.lower_bound:
            self.monster_lists.append(monsters)

    def get_lists_of_correct_occurrence(self):
        if self.occurrence == 'all':
            return self.monster_lists
        probabilities = {'common': 0.7, 'uncommon': 0.3, 'rare': 0.1}
        p = probabilities[self.occurrence]
        monster_lists = []
        for monster_list in self.monster_lists:
            ps = [probabilities[name['occurrence']] for name in monster_list]
            if any([p_ == p for p_ in ps]) and not any([p_ < p for p_ in ps]):
                monster_lists.append(monster_list)
        return monster_lists

    def adjusted_xp(self):
        return int(self.adjust_xp_for_monster_counts(self.total_xp(), adjust=0))

    def total_xp(self):
        return int(sum([monster['XP'] for monster in self.monsters]))