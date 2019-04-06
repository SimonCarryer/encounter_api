from .xp_calculator import XPCalulator
from random import Random

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
                'tags': self.encounter_tags(monster_list),
                'monsters': monster_list,
                'xp_value': self.xp_calculator.adjusted_xp_sum(monster_list)
            }
            for monster in monster_list:
                self.monsters[monster['occurrence']].add(monster['Name'])
            self.encounters.append(encounter)

    def encounter_occurrence(self, monster_set):
        max_occurrence = max([occurrence_dict[monster['occurrence']] for monster in monster_set])
        return reverse_occurrence_dict[max_occurrence]

    def encounter_difficulty(self, monster_set):
        xp_value = self.xp_calculator.adjusted_xp_sum(monster_set)
        relative_difficulty = xp_value / self.xp_budget
        if relative_difficulty <= 0.5:
            difficulty = 'trivial'
        elif relative_difficulty <= 0.8:
            difficulty = 'easy'
        elif relative_difficulty <= 1.2:
            difficulty = 'medium'
        elif relative_difficulty <= 1.5:
            difficulty = 'hard'
        else:
            difficulty = 'deadly'
        return difficulty

    def encounter_tags(self, monster_set):
        roles = set([m['role'] for m in monster_set])
        tags = list(roles)
        if 'leader' not in roles:
            tags.append('no leader')
        if 'pet' not in roles:
            tags.append('no pets')
        if roles != set(['pet']):
            tags.append('not just pets')
        if not any([role in roles for role in ['environmental hazard', 'pet', 'leader']]):
            tags.append('basic')
        if roles == set(['pet']):
            tags.append('just pets')
        return tags

    def score_encounter(self, difficulty, occurrence, style, preferred_monster, encounter):
        score = 0
        if encounter['difficulty'] == difficulty:
            score += 2
        if encounter['occurrence'] == occurrence:
            score += 1
        if style in encounter['tags']:
            score += 3
        if preferred_monster in [m['Name'] for m in encounter['monsters']]:
            score += 1
        return score

    def top_encounters(self, difficulty, occurrence, style, preferred_monster):
        encounter_scores = [(self.score_encounter(difficulty, occurrence, style, preferred_monster, encounter), encounter) for encounter in self.encounters]
        max_score = max([score for score, encounter in encounter_scores])
        top_encounters = [encounter for score, encounter in encounter_scores if score == max_score]
        while len(top_encounters) == 0:
            max_score -= 1
            top_encounters += [encounter for score, encounter in encounter_scores if score == max_score]
        return top_encounters

    def pick_encounter(self, difficulty=None, occurrence=None, style=None):
        if occurrence is None:
            roll = self.random_state.randint(1, 6)
            if roll <= 3:
                occurrence = 'common'
            elif roll <= 5:
                occurrence = 'uncommon'
            else:
                occurrence = 'rare'
        if style is None:
            roll = self.random_state.randint(1, 6)
            if roll == 1:
                style = None
            elif roll == 2:
                style = 'no pets'
            elif roll == 3:
                style = 'basic'
            elif roll == 4:
                style = 'not just pets'
            elif roll == 5:
                style = 'elite'
            elif roll == 6:
                style = 'leader'
        if len(self.monsters[occurrence]) > 0:
            preferred_monster = self.random_state.choice(list(self.monsters[occurrence]))
        else:
            preferred_monster = None
        if len(self.encounters) == 0:
            return {'monsters': []}
        else:
            top_encounters = self.top_encounters(difficulty, occurrence, style, preferred_monster)
            pick = self.random_state.choice(top_encounters)
            roles = set([monster['role'] for monster in pick['monsters']])
            return pick
            
        

    

        