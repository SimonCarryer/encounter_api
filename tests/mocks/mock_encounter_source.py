
class MockEncounterSource:
    def __init__(self):
        self.monster_set = 'mock'

    def get_encounter(self, style=None, difficulty=None, occurrence=None):
        return {'monsters': 'Some scary monsters', 'success': True, 'style': style}

    def get_sign(self):
        return 'a sign of some scary monsters'

class MockMonsterManual:
    def get_rumours(self, monster_set, populator_type):
        return ['A test rumour']

class MockDungeonManager:
    def __init__(self):
        self.encounter_source = MockEncounterSource()
        self.monster_manual = MockMonsterManual()

    def get_encounter(self, name, **kwargs):
        encounter = self.encounter_source.get_encounter(**kwargs)
        encounter['source'] = name
        return encounter

    def add_encounter_source(self, name, set, event_description, wandering=False):
        pass

    def get_sign(self, name):
        return self.encounter_source.get_sign()

    def add_event(self, *args, **kwargs):
        pass

    def get_treasure(self, shares=1):
        return 'Some cool treasure'

    def get_monster_sets(self, **kwargs):
        return ['goblins', 'kobolds']
