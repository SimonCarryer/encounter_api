
class MockEncounterSource:
    def __init__(self):
        pass

    def get_encounter(self, style=None, difficulty=None, occurrence=None):
        return {'monsters': 'Some scary monsters', 'success': True, 'style': style}
