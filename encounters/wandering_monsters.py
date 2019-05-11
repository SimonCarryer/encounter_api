from .encounter_api import EncounterSource
from random import Random
from collections import defaultdict

class WanderingMonsters:
    def __init__(self, level, monster_sets, random_state=None, die_type=6):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.die_type = die_type
        self.level = level
        self.monster_sets = monster_sets
        self.encounters = self.get_encounters()
        self.table = self.build_table()

    def get_encounters(self):
        encounters = []
        for monster_set in sorted(self.monster_sets):
            source = EncounterSource(encounter_level=self.level, monster_sets=[monster_set], random_state=self.random_state)
            for _ in range(self.die_type):
                encounter = source.get_encounter(difficulty='easy', style='basic', occurrence='common')
                if encounter['success']:
                    encounters.append(encounter)
        return encounters

    def build_table(self):
        if len(self.encounters) >= self.die_type:
            encounters = self.random_state.sample(self.encounters, self.die_type)
            counts = defaultdict(int)
            for encounter in encounters:
                counts[encounter['monster_hash']] += 1
            i = 0
            if len(counts) > 1:
                table = []
                for monster_hash, count in counts.items():
                    encounter = [encounter for encounter in encounters if encounter['monster_hash'] == monster_hash][0]
                    if count > 1:
                        roll = ' - '.join([str(i+1), str(i+count)])
                    else:
                        roll = i+1
                    table.append({'roll': roll, 'monsters': encounter['monsters']})
                    i += count
            else:
                monster_hash = list(counts.keys())[0]
                encounter = [encounter for encounter in encounters if encounter['monster_hash'] == monster_hash][0]
                table = [{'roll': 'Enounter', 'monsters': encounter['monsters']}]
        else:
            table = None
        return table



        


    
