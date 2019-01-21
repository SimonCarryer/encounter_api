import csv
import yaml
from random import Random
import copy


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

def load_environment_tags():
    monster_dict = load_monster_manual()
    with open('data/environment_tags.yaml') as f:
        environment_tags = yaml.load(f.read())
    for tag in environment_tags.keys():
        amended_monsters = []
        for monster in environment_tags[tag]['monsters']:
            monster_data = monster_dict.get(monster['Name'])
            if monster_data is not None:
                merged_data = {**monster, **monster_data}
                merged_data['XP'] = int(merged_data['XP'])
                if merged_data.get('role') is None:
                    merged_data['role'] = 'natural hazard'
                amended_monsters.append(merged_data)
            else:
                print('uh oh!: %s not loaded' % monster)
        environment_tags[tag]['monsters'] = amended_monsters
    return environment_tags

environment_tags = load_environment_tags()
    
class MonsterManual():
    def __init__(self):
        self.name = None
        self.environment_tags = copy.deepcopy(environment_tags)
        self.monster_sets = [key for key in self.environment_tags.keys()]

    def monsters(self, monster_set_name, random_state):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        if monster_set_name is None:
            monster_set_name = self.random_state.choice(self.monster_sets)
        self.name = monster_set_name
        monster_set = self.environment_tags[monster_set_name]['monsters']
        return monster_set