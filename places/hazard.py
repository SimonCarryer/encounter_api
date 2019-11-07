from random import Random
from string import Template
import yaml
from bisect import bisect_left


with open('data/hazards.yaml') as f:
    hazards = yaml.load(f)

with open('data/traps.yaml') as f:
    attacks = {}
    saves = {}
    effects = {}
    triggers = {}
    telltales = {}
    trap_file = yaml.load(f)
    damage = trap_file['damage']
    for challenge in ['setback', 'dangerous', 'deadly']:
        attacks[challenge] = tuple([int(i) for i in trap_file['attack'][challenge].split(', ')])
        saves[challenge] = tuple([int(i) for i in trap_file['save'][challenge].split(', ')])

def get_hazard_damage(level):
    levels = list(damage.keys())
    idx = bisect_left(levels, level)
    return damage[levels[idx]]

class Hazard:
    def __init__(self, level, hazard_type, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        self.template = Template(hazards['hazard types'][hazard_type]['description'])
        self.challenge = hazards['hazard types'][hazard_type]['challenge']
        self.damage = get_hazard_damage(self.level)[self.challenge]
        self.beneficial_magic = self.random_state.choice(hazards['effects']['beneficial_magic'])
        self.harmful_magic = self.random_state.choice(hazards['effects']['harmful_magic'])
        self.plants = self.random_state.choice(hazards['effects']['plants'])
        self.save = self.choose_save()

    def choose_save(self):
        return self.random_state.randint(*saves[self.challenge])
        

    def __str__(self):
        d = {
            'beneficial_magic': self.beneficial_magic,
            'harmful_magic': self.harmful_magic,
            'damage': self.damage,
            'plants': self.plants,
            'save': self.save
        }
        s = self.template
        while '$' in s.template:
            s = Template(s.safe_substitute(d))
        return s.template