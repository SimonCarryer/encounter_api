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
    def __init__(self):
        self.name = None
        self.monster_sets = copy.deepcopy(monster_sets)
        self.monster_set_names = [key for key in self.monster_sets.keys()]

    def monsters(self, monster_set_name, random_state):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        if monster_set_name is None:
            monster_set_name = self.random_state.choice(self.monster_set_names)
        self.name = monster_set_name
        monster_set = self.monster_sets[monster_set_name]
        return monster_set