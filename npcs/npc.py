from random import Random
from names.name_api import NameGenerator
from treasure.npc_items import NPC_item
import yaml

with open('data/npc_traits.yaml') as f:
    traits = yaml.load(f)
    
with open('data/npc_roles.yaml') as f:
    roles = yaml.load(f)

class NPC:
    def __init__(self, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.role = self.random_state.choice(list(roles.keys()))
        self.sex = self.random_state.choice(['male', 'female', 'male', 'female', 'other'])
        self.traits = {}
        for trait in roles[self.role].keys():
            self.traits[trait] = self.random_state.choice(roles[self.role][trait])
        for trait in self.random_state.sample(traits.keys(), 3):
            self.traits[trait] = self.random_state.choice(traits[trait])
        self.name = NameGenerator(random_state=self.random_state).simple_person_name(sex=self.sex)
        if self.random_state.randint(1, 6) >= 5:
            self.traits['item'] = NPC_item(level=5, random_state=self.random_state).item

    def details(self):
        return {
            'traits': self.traits,
            'role': self.role,
            'sex': self.sex,
            'name': self.name
        }