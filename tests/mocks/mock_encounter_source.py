
class MockEncounterSource:
    def __init__(self):
        pass

    def get_encounter(self, style=None, difficulty=None, occurrence=None):
        return {'monsters': 'Some scary monsters', 'success': True, 'style': style}

    def get_sign(self):
        return 'a sign of some scary monsters'

class MockEncounterManager:
    def __init__(self):
        self.encounter_source = MockEncounterSource()

    def get_encounter(self, name, **kwargs):
        encounter = self.encounter_source.get_encounter(**kwargs)
        encounter['source'] = name
        return encounter

    def add_encounter_source(self, name, something_else):
        pass

    def get_sign(self, name):
        return self.encounter_source.get_sign()
