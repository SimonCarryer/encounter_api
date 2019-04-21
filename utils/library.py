from monster_manual.monster_manual import MonsterManual
from tests.mocks.mock_monster_list import MockMonsterManual

monster_manual = MonsterManual()

def use_mock_monster_manual():
    global monster_manual
    monster_manual = MockMonsterManual()

def use_real_monster_manual():
    global monster_manual
    monster_manual = MonsterManual()