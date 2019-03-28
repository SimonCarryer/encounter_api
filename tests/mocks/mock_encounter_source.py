class MockEncounterSource:
    def get_encounter(self, style=None):
        return {'monsters': 'Some scary monsters', 'success': True, 'style': style}