class MockTreasureSource:
    def get_treasure(self, shares=1):
        return {'coins': '%d coins' % shares}