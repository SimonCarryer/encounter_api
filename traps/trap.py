import yaml
from random import Random
from bisect import bisect_left
from string import Template
from utils import library
from encounters.encounter_api import EncounterSource

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
    for trap_class in ['mechanical', 'magical']:
        telltales[trap_class] = trap_file[trap_class]['telltales']
        effects[trap_class] = trap_file[trap_class]['effect']
        triggers[trap_class] = trap_file[trap_class]['trigger']

def get_trap_damage(level):
    levels = list(damage.keys())
    idx = bisect_left(levels, level)
    return damage[levels[idx]]

def get_trap_effects(level, trap_class):
    levels = list(effects[trap_class].keys())
    idx = bisect_left(levels, level)
    return effects[trap_class][levels[idx]]


class Trap:
    def __init__(self, level, challenge=None, trap_class=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.level = level
        if challenge is None:
            roll = self.random_state.randint(1, 6)
            if roll <= 3:
                self.challenge = 'setback'
            elif roll <= 5:
                self.challenge = 'dangerous'
            else:
                self.challenge = 'deadly'
        else:
            self.challenge = challenge
        if trap_class is None:
            self.trap_class = self.random_state.choice(['mechanical', 'magical'])
        else:
            self.trap_class = trap_class
        self.attack = self.choose_attack()
        self.spot = self.choose_save()
        self.save = self.choose_save()
        self.damage = get_trap_damage(self.level)[self.challenge]
        self.trigger = self.random_state.choice(triggers[self.trap_class])
        self.telltale = self.random_state.choice(telltales[self.trap_class])
        effect = self.random_state.choice(get_trap_effects(self.level, self.trap_class))
        self.name = effect['name']
        self.template = Template('$name trap: Triggered by $trigger. Can be detected by noticing $telltale (DC$spot). ' + effect['effect'])

    def choose_attack(self):
        return self.random_state.randint(*attacks[self.challenge])
    
    def choose_save(self):
        return self.random_state.randint(*saves[self.challenge])

    def summon_monsters(self):
        if self.challenge == 'setback':
            difficulty = 'easy'
        elif self.challenge == 'dangerous':
            difficulty = 'medium'
        else:
            difficulty = 'hard'
        sets = library.monster_manual.get_monster_sets(any_tags=['fiend', 'celestial', 'elemental'], level=self.level)
        if len(sets) == 0:
            sets = library.monster_manual.get_monster_sets(any_tags=['elemental'], level=None)
        encounter = EncounterSource(encounter_level=self.level, monster_sets=sets).get_encounter(style='basic', difficulty=difficulty)
        monsters = ', '.join(['%s: %d' % (m['name'], m['number']) for m in encounter['monsters']])
        return monsters

    def __str__(self):
        d = {
            'name': self.name,
            'telltale': self.telltale,
            'spot': self.spot,
            'trigger': self.trigger,
            'damage': self.damage,
            'save': self.save,
            'attack': self.attack,
            'monsters': self.summon_monsters()
        }
        return self.template.substitute(d)
        
