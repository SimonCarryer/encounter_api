import csv
import yaml
from random import Random
import copy

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

with open('data/rumours.yaml', 'r') as f:
    monster_rumours = yaml.load(f)

with open('data/dragons.yaml', 'r') as f:
    dragons = yaml.load(f)


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
    with open('data/monster_sets.yaml') as f:
        monster_sets = yaml.load(f.read())
    for tag in monster_sets.keys():
        amended_monsters = []
        for monster in monster_sets[tag]:
            monster = add_data_to_monster(monster)
            if monster is not None:
                amended_monsters.append(monster)
        monster_sets[tag] = amended_monsters
    return monster_sets


def add_data_to_monster(monster):
    monster_data = copy.deepcopy(monster_dict.get(monster['Name']))
    if monster_data is not None:
        monster.update(monster_data)
        monster['XP'] = int(monster['XP'])
        if monster.get('role') is None:
            monster['role'] = 'natural hazard'
        return monster
    else:
        print('uh oh!: %s not loaded' % monster)
        return None


monster_dict = load_monster_manual()
monster_sets = load_monster_sets()


class MonsterManual():
    def __init__(self, terrain=None):
        self.terrain = terrain
        self.monster_sets = copy.deepcopy(monster_sets)
        self.monster_set_names = [key for key in self.monster_sets.keys()]
        self.monster_tags = copy.deepcopy(monster_tags)
        self.terrain = terrain
        if terrain is not None:
            self.add_dragons()
        self.tags = set([tag for tags in self.monster_tags.values()
                         for tag in tags])

    def monsters(self, monster_set_name):
        monster_set = copy.deepcopy(self.monster_sets[monster_set_name])
        return sorted(monster_set, key=lambda x: x['Name'])

    def get_monster_set_by_tags(self, list_of_tags, monster_sets=None, any_or_all=any, exclude=False):
        if list_of_tags is None:
            list_of_tags = []
        if monster_sets is None:
            monster_sets = self.monster_set_names
        if exclude:
            def filter_sets(x): return not any_or_all(x)
        else:
            def filter_sets(x): return any_or_all(x)
        sets = []
        for monster_set in monster_sets:
            set_tags = self.monster_tags.get(monster_set, [])
            if filter_sets([tag in set_tags for tag in list_of_tags]):
                sets.append(monster_set)
        return sets

    def get_monster_sets(self, all_tags=None, any_tags=None, none_tags=None, level=None, sets=None):
        if sets is None:
            terrain_tags = ['any terrain', 'underdark']
            if self.terrain is not None:
                terrain_tags.append(self.terrain)
            else:
                terrain_tags += [
                    "forest",
                    "desert",
                    "mountains",
                    "arctic",
                    "plains",
                    "hills",
                    "jungle",
                    "swamp",
                    "underwater",
                    "urban"
                ]
            sets = self.get_monster_set_by_tags(
                terrain_tags, monster_sets=sets, any_or_all=any)
        if all_tags is not None:
            sets = self.get_monster_set_by_tags(
                all_tags, monster_sets=sets, any_or_all=all)
        if any_tags is not None:
            sets = self.get_monster_set_by_tags(
                any_tags, monster_sets=sets, any_or_all=any)
        if none_tags is not None:
            sets = self.get_monster_set_by_tags(
                none_tags, monster_sets=sets, any_or_all=any, exclude=True)
        if level is not None:
            sets = [monster_set for monster_set in sets if self.appropriate_challenge(
                monster_set, level)]
        return sorted(list(sets))

    def get_tags(self):
        return sorted(list(self.tags))

    def appropriate_challenge(self, monster_set, level):
        mob_monster_levels = [level_lookup[monster['XP']] for monster in self.monster_sets[monster_set]
                              if monster['role'] in ['natural hazard', 'troops'] and monster['occurrence'] != 'rare']
        good_challenge_mobs = [monster_level for monster_level in mob_monster_levels if monster_level <
                               level-0.5 and monster_level >= (level/10)-0.5]
        boss_monster_levels = [level_lookup[monster['XP']] for monster in self.monster_sets[monster_set]
                               if monster['role'] in ['leader', 'solo'] and monster['occurrence'] != 'rare']
        good_challenge_bosses = [
            monster_level for monster_level in boss_monster_levels if monster_level <= level and monster_level >= level-8]
        return (len(mob_monster_levels) == 0 or len(good_challenge_mobs) > 0) and (len(boss_monster_levels) == 0 or len(good_challenge_bosses) > 0)

    def get_signs(self, monster_set):
        tags = monster_tags[monster_set]
        signs = []
        for sign in copy.deepcopy(monster_signs):
            if all([tag in tags for tag in sign['tags']]):
                sign = sign['sign']
                signs.append(sign)
        return signs

    def get_rumours(self, monster_set, populator_type):
        tags = monster_tags[monster_set]
        rumours = []
        for rumour in copy.deepcopy(monster_rumours[populator_type]):
            if all([tag in tags for tag in rumour['tags']]):
                rumour = rumour['description']
                rumours.append(rumour)
        return rumours

    def add_dragons(self):
        dragon_list = [add_data_to_monster(dragon)
                       for dragon in dragons[self.terrain]]
        self.monster_sets['apex predators'] += dragon_list
