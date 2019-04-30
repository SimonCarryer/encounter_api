import csv
import yaml
from random import Random
import copy
import numpy as np

with open('data/xp_values.yaml') as f:
    xp_values = yaml.load(f.read())
    level_lookup = {value: key for key, value in xp_values.items()}

with open('data/monster_tags.yaml') as f:
    monster_tags = yaml.load(f.read())

with open('data/monster_signs.yaml') as f:
    monster_signs = []
    for idx, sign_data in enumerate(yaml.load(f.read())):
        sign_data.update({'idx': idx})
        sign_data['tags'] = sign_data.get('tags', [])
        sign_data['sign'] = sign_data.get('sign', '')
        monster_signs.append(sign_data)

def load_monster_manual():
    monster_dict = {}
    with open('data/monsters.csv', 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            monster_dict[row['Name']] = row
    with open('data/npcs.csv', 'r') as csvfile:
        csv_reader = csv.DictReader(csvfile)
        for row in csv_reader:
            monster_dict[row['Name']] = row
    return monster_dict

def load_monster_sets():
    monster_dict = load_monster_manual()
    with open('data/monster_sets.yaml') as f:
        monster_sets = yaml.load(f.read())
    for tag in monster_sets.keys():
        amended_monsters = []
        for monster in monster_sets[tag]:
            monster_data = monster_dict.get(monster['Name'])
            if monster_data is not None:
                monster.update(monster_data)
                monster['XP'] = int(monster['XP'])
                if monster.get('role') is None:
                    monster['role'] = 'natural hazard'
                amended_monsters.append(monster)
            else:
                print('uh oh!: %s not loaded' % monster)
        monster_sets[tag] = amended_monsters
    return monster_sets

monster_sets = load_monster_sets()

    
class MonsterManual():
    def __init__(self, terrain=None):
        self.terrain = terrain
        self.monster_sets = monster_sets
        self.monster_set_names = [key for key in self.monster_sets.keys()]
        self.monster_tags = copy.deepcopy(monster_tags)
        if terrain is not None:
            self.monster_sets = {key: monster_sets[key] for key in self.get_monster_sets(any_tags=[terrain, 'any terrain', 'underdark'])}
            self.monster_set_names = [key for key in self.monster_sets.keys()]
        self.tags = set([tag for tags in self.monster_tags.values() for tag in tags])

    def monsters(self, monster_set_name):
        monster_set = copy.deepcopy(self.monster_sets[monster_set_name])
        return monster_set

    def get_monster_set_by_tags(self, list_of_tags, monster_sets=None, any_or_all=any, exclude=False):
        if list_of_tags is None:
            list_of_tags = []
        if monster_sets is None:
            monster_sets = self.monster_set_names
        if exclude:
            filter_sets = lambda x: not any_or_all(x)
        else:
            filter_sets = lambda x: any_or_all(x)
        sets = []
        for monster_set in monster_sets:
            set_tags =  self.monster_tags.get(monster_set, [])
            if filter_sets([tag in set_tags for tag in list_of_tags]):
                sets.append(monster_set)
        return sets

    def get_monster_sets(self, all_tags=None, any_tags=None, none_tags=None, level=None, sets=None):
        if sets is None:
            sets = self.monster_set_names
        if all_tags is not None:
            sets = self.get_monster_set_by_tags(all_tags, monster_sets=sets, any_or_all=all)
        if any_tags is not None:
            sets = self.get_monster_set_by_tags(any_tags, monster_sets=sets, any_or_all=any)
        if none_tags is not None:
            sets = self.get_monster_set_by_tags(none_tags, monster_sets=sets, any_or_all=any, exclude=True)
        if level is not None:
            sets = [monster_set for monster_set in sets if self.appropriate_challenge(monster_set, level)]
        return sorted(list(sets))

    def get_tags(self):
        return sorted(list(self.tags))

    def appropriate_challenge(self, monster_set, level):
        mob_monster_levels = [level_lookup[monster['XP']] for monster in self.monster_sets[monster_set] if monster['role'] in ['natural hazard', 'troops']]
        good_challenge_mobs = [monster_level for monster_level in mob_monster_levels if monster_level < level-0.5 and monster_level >= (level/12)-0.5]
        boss_monster_levels = [level_lookup[monster['XP']] for monster in self.monster_sets[monster_set] if monster['role'] in ['leader', 'solo']]
        good_challenge_bosses = [monster_level for monster_level in boss_monster_levels if monster_level <= level+1 and monster_level >= level-2]
        number_of_monsters = len(good_challenge_mobs + good_challenge_bosses)
        return number_of_monsters > 0

    def get_signs(self, monster_set):
        tags = monster_tags[monster_set]
        signs = []
        for sign in copy.deepcopy(monster_signs):
            if all([tag in tags for tag in sign['tags']]):
                sign = sign['sign'] + ' (%s)' % monster_set
                signs.append(sign)
        return signs