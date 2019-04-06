
class MockEncounterSource:
    def __init__(self, monster_source):
        self.monster_source = monster_source

    def get_encounter(self, style=None, difficulty=None, occurrence=None):
        return {'monsters': 'Some scary monsters', 'success': True, 'style': style}

    def get_sign(self):
        return self.monster_source.signs()