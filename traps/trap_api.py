from .trap import Trap
from random import Random

class TrapSource:
    def __init__(self, level, trap_class=None, random_state=None):
        if random_state is None:
            self.random_state = Random()
        self.level = level
        self.trap_class = trap_class

    def get_trap(self, challenge=None, trap_class=None):
        if trap_class is None:
            trap_class = self.trap_class
        return str(Trap(self.level, trap_class=trap_class, challenge=challenge, random_state=self.random_state))
