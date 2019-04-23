class MockTrapSource:
    def get_trap(self, challenge=None):
        return 'A nasty trap, with challenge %s' % challenge