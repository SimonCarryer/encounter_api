from .xp_calculator import XPCalulator
from random import Random
from hashlib import md5
from collections import defaultdict


occurrence_dict = {'common': 1, 'uncommon': 2, 'rare': 3}
reverse_occurrence_dict = {v: k for k, v in occurrence_dict.items()}

class EncounterPicker:
    def __init__(self,
                 encounters,
                 xp_budget,
                 n_characters=4,
                 random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.xp_calculator = XPCalulator(n_characters=n_characters)
        self.xp_budget = xp_budget
        self.encounters = []
        self.monsters = {'rare': set(),
                          'uncommon': set(),
                          'common': set()}
        for monster_list in encounters:
            encounter = {
                'difficulty': self.encounter_difficulty(monster_list),
                'occurrence': self.encounter_occurrence(monster_list),
                'style': self.encounter_style(monster_list),
                'monsters': monster_list,
                'xp_value': self.xp_calculator.adjusted_xp_sum(monster_list),
                'monster_hash': self.hash_monsters([m['Name'] for m in monster_list])
            }
            for monster in monster_list:
                if monster['role'] not in ['environmental hazard', 'pet']:
                    self.monsters[monster['occurrence']].add(monster['Name'])
            self.encounters.append(encounter)
        self.difficulty_weight = 4
        self.style_weight = 8
        self.occurrence_weight = 2
        self.preferred_monster_weight = 1
        self.set_modifier = 16
        self.used_monster_weight = 2
        self.used_encounters = defaultdict(int)

    def hash_monsters(self, monsters):
        hashed = md5(''.join(sorted(tuple(set(monsters)))).encode())
        return hashed.hexdigest()

    def encounter_occurrence(self, monster_set):
        max_occurrence = max([occurrence_dict[monster['occurrence']] for monster in monster_set])
        return reverse_occurrence_dict[max_occurrence]

    def encounter_difficulty(self, monster_set):
        xp_value = self.xp_calculator.adjusted_xp_sum(monster_set)
        relative_difficulty = xp_value / self.xp_budget
        if relative_difficulty <= 0.5:
            difficulty = 'Trivial'
        elif relative_difficulty <= 0.8:
            difficulty = 'Easy'
        elif relative_difficulty <= 1.2:
            difficulty = 'Medium'
        elif relative_difficulty <= 1.5:
            difficulty = 'Hard'
        else:
            difficulty = 'Deadly'
        return difficulty

    def encounter_style(self, monster_set):
        roles = [monster['role'] for monster in monster_set]
        if 'leader' in roles or 'solo' in roles:
            style = 'leader'
        elif not any([role in roles for role in ['environmental hazard', 'pet', 'leader']]):
            style = 'basic'
        else:
            style = 'exotic'
        return style

    def score_encounter(self, difficulty, occurrence, style, preferred_monster, encounter, weights):
        score = 0
        if encounter['difficulty'] == difficulty:
            score += weights['difficulty']
        if encounter['occurrence'] == occurrence:
            score += weights['occurrence']
        if style == encounter['style']:
            score += weights['style']
        if preferred_monster in [m['Name'] for m in encounter['monsters']]:
            score += weights['preferred_monster']
        score -= self.used_encounters[encounter['monster_hash']] * self.used_monster_weight
        return score

    def top_encounters(self, difficulty, occurrence, style, preferred_monster, weights):
        encounter_scores = [(self.score_encounter(difficulty, occurrence, style, preferred_monster, encounter, weights), encounter) for encounter in self.encounters]
        max_score = max([score for score, encounter in encounter_scores])
        top_encounters = [encounter for score, encounter in encounter_scores if score == max_score]
        return top_encounters

    def pick_encounter(self, difficulty=None, occurrence=None, style=None):
        weights = {
            'difficulty': self.difficulty_weight,
            'occurrence': self.occurrence_weight,
            'style': self.style_weight,
            'preferred_monster': self.preferred_monster_weight
        }
        if occurrence is None:
            roll = self.random_state.randint(1, 6)
            if roll <= 3:
                occurrence = 'common'
            elif roll <= 5:
                occurrence = 'uncommon'
            else:
                occurrence = 'rare'
        else:
            weights['occurrence'] += self.set_modifier
        if style is None:
            roll = self.random_state.randint(1, 6)
            if roll <= 3:
                style = 'basic'
            elif roll <= 5:
                style = 'exotic'
            elif roll == 6:
                style = 'leader'
        else:
            weights['style'] += self.set_modifier
        if len(self.monsters[occurrence]) > 0:
            preferred_monster = self.random_state.choice(sorted(list(self.monsters[occurrence])))
        else:
            preferred_monster = None
        if len(self.encounters) == 0:
            return {'monsters': []}
        else:
            top_encounters = self.top_encounters(difficulty, occurrence, style, preferred_monster, weights)
            pick = self.random_state.choice(top_encounters)
            roles = set([monster['role'] for monster in pick['monsters']])
            self.used_encounters[pick['monster_hash']] += 1
            return pick
            
        

    

        