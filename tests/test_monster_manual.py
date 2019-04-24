from monster_manual.monster_manual import MonsterManual
from utils import library

def test_get_monster_set_by_tags():
    mm = MonsterManual()
    tags = ['savage', 'dungeon-explorer']
    sets = mm.get_monster_set_by_tags(tags, any_or_all=all)
    desired = ['bugbears', 'hobgoblins', 'orcs', 'goblins', 'gnolls', 'kobolds']
    assert all(set_ in sets for set_ in desired)

def test_exclude_monster_set_by_tags():
    mm = MonsterManual()
    desired_tags = ['dungeon-explorer']
    sets = mm.get_monster_set_by_tags(desired_tags, any_or_all=any)
    assert('goblins' in sets)
    assert('cult of baphomet' in sets)
    undesired_tags = ['human']
    sets = mm.get_monster_set_by_tags(undesired_tags, monster_sets=sets, any_or_all=any, exclude=True)
    assert('goblins' in sets)
    assert('cult of baphomet' not in sets)

def test_get_monster_sets():
    mm = MonsterManual()
    sets = mm.get_monster_sets(any_tags=['evil', 'forest'], all_tags=['humanoid'], none_tags=['human'])
    desired = ['forest goblins', 'yuan-ti', 'gnolls', 'drow']
    undesired = ['bandits', 'cult of obox-ob', 'blights', 'bullywugs']
    assert all(set_ in sets for set_ in desired)
    assert not any(set_ in sets for set_ in undesired)

def test_get_monster_set_level():
    mm = MonsterManual()
    for level in range(1, 21):
        print(sorted(mm.get_monster_sets(all_tags=['cave-dweller'], none_tags=['underdark'], level=level)))

def test_get_sings():
    mm = MonsterManual()
    # for sign in mm.get_signs('bugbears'):
    #     print(sign)





