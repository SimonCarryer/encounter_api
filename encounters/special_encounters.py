import yaml
from .encounter_api import EncounterSource
from monster_manual import monster_manual

with open('data/encounter_modifiers.yaml', 'r') as f:
    encounter_traits = yaml.load(f)

class SpecialEncounter(EncounterSource):
    def pick_trait(self, monster_set):
        monster_set_tags = monster_manual.monster_tags[monster_set]
        possible_traits = []
        for trait in encounter_traits:
            if all([trait_tag in monster_set_tags for trait_tag in trait['tags']]) or trait['tags'] == []:
                possible_traits.append(trait)
        if len(possible_traits) > 0:
            trait = self.random_state.choice(possible_traits)
        else:
            trait = None
        return trait

    def assign_special_trait(self, encounter):
        monster = self.random_state.choice(encounter['monsters'])
        trait = self.pick_trait(encounter['monster_set'])
        if trait is not None:
            description = 'Any %s in this encounter has the following trait: %s. %s' % (monster['name'], trait['name'], trait['description'])
        else:
            description = ''
        return description

