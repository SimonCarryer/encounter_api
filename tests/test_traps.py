from traps.trap import *
from traps.trap_api import TrapSource

def test_trap_data():
    #print(damage)
    pass

def test_get_damage():
    assert get_trap_damage(1)['setback'] == 1
    assert get_trap_damage(10)['setback'] == 2

def test_set_trap_values():
    trap = Trap(3, trap_class='magical')
    #print(trap)

def test_trap_summon():
    trap = Trap(11)
    #print(trap.summon_monsters())

def test_trap_api():
    source = TrapSource(5)
    #print(source.get_trap())
