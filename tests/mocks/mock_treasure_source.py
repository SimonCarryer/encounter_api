class MockTreasureSource:
    def get_treasure(self, shares=1):
        return {'coins': '%d coins' % shares}

class MockRawHoardSource:
    def get_treasure(self):
        return [('GP', 100), ('magic item', 'something cool'), ('gem', 20), ('object', 100), ('SP', 1000)]