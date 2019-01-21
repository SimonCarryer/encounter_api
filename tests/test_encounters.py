from encounters import Encounter, EncounterSource
from tests.mocks.mock_monster_list import mock_monster_list, mock_monster_list_2, MockMonsterManual
from random import Random


def test_right_role():
    budget = 450
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list)
    right_roles = [m['Name'] for m in encounter.right_role([])]
    assert right_roles == ['boss monster', 'trooper', 'fancy man', 'extra fancy man', 'doggo']

def test_right_idx():
    budget = 450
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list)
    right_idx = [m['Name'] for m in encounter.right_index_monsters([])]
    assert right_idx == ['boss monster', 'trooper', 'fancy man', 'extra fancy man', 'doggo']

def test_possible_monsters():
    budget = 450
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, respect_roles=False, occurrence='all')
    possible = [monster['Name'] for monster in encounter.possible_monsters([])]
    assert possible == ['boss monster', 'trooper', 'fancy man', 'extra fancy man', 'doggo']

def test_encounter_gets_unique_combinations():
    budget = 450
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list)
    assert len(encounter.monster_lists) == 9

def test_encounter_can_be_deterministic():
    budget = 450
    monsters = []
    for _ in range(10):
        random_state = Random(4)
        encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, random_state=random_state, occurrence='all')
        monsters.append(encounter.monsters)
    assert all([monster_set[0]['Name'] == 'doggo' for monster_set in monsters])

def test_calculate_adjustment():
    encounter = Encounter(xp_budget=200, monster_source=mock_monster_list)
    adjustments = [(i, encounter.calculate_adjustment(i)) for i in range(0, 20)]
    assert adjustments == [(0, 1), (1, 1), (2, 1.5), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2.5), (8, 2.5), (9, 2.5), (10, 2.5), (11, 3), (12, 3), (13, 3), (14, 3), (15, 4), (16, 4), (17, 4), (18, 4), (19, 4)]

def test_encounter_does_not_exceed_xp_budget():
    xp_values = []
    budget = 450
    maximum = budget * 1.5
    for _ in range(10):
        encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='all')
        xp_values.append(encounter.adjusted_xp())
    assert all([xp <= maximum for xp in xp_values])
    budget = 1000
    maximum = budget * 1.5
    for _ in range(10):
        encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='all')
        xp_values.append(encounter.adjusted_xp())
    assert all([xp <= maximum for xp in xp_values])


def test_encounter_never_below_threshold_of_xp_budget():
    xp_values = []
    budget = 450
    minimum = budget*0.5
    for _ in range(10):
        encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='all')
        xp_values.append(encounter.adjusted_xp())
    assert all([xp >= minimum for xp in xp_values])
    xp_values = []
    budget = 1000
    minimum = budget*0.5
    for _ in range(10):
        encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='all')
        xp_values.append(encounter.adjusted_xp())
    assert all([xp >= minimum for xp in xp_values])

def test_correct_lists_generated():
    budget = 450
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='all')
    correct =  [['boss monster'], 
                ['doggo', 'trooper', 'trooper'], 
                ['fancy man', 'trooper'], 
                ['doggo', 'doggo', 'doggo', 'trooper'], 
                ['doggo', 'doggo', 'trooper'], 
                ['doggo', 'fancy man'], 
                ['extra fancy man'], 
                ['doggo', 'doggo', 'doggo', 'doggo', 'doggo'], 
                ['doggo', 'doggo', 'doggo', 'doggo']]
    returned = [[m['Name'] for m in l] for l in encounter.monster_lists]
    assert returned == correct

def test_roles_respected():
    budget = 1500
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='all')
    returned = [[m['Name'] for m in l] for l in encounter.monster_lists]
    assert ('fancy man', 'extra fancy man') not in returned
    assert ('boss monster', 'boss monster') not in returned
    budget = 450
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='all')
    # assert ('doggo', 'doggo', 'doggo', 'doggo') not in encounter.monster_lists
    budget = 200
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list_2, occurrence='all')
    returned = [[m['Name'] for m in l] for l in encounter.monster_lists]
    assert returned == [['nature boy', 'nature boy', 'nature boy', 'nature boy'], ['nature girl', 'nature girl', 'nature girl', 'nature girl']]
    budget = 50
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list_2, occurrence='all')
    returned = [[m['Name'] for m in l] for l in encounter.monster_lists]
    assert returned == [['lonely man']]
 
def test_get_lists_of_correct_occurrence():
    budget = 450
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='rare')
    returned = [[m['Name'] for m in l] for l in encounter.get_lists_of_correct_occurrence()]
    assert returned == [['extra fancy man']]
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, occurrence='uncommon')
    returned = [[m['Name'] for m in l] for l in encounter.get_lists_of_correct_occurrence()]
    assert all(['doggo' in l or 'fancy_man' in l for l in returned])
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list, respect_roles=True, occurrence='common')
    returned = [[m['Name'] for m in l] for l in encounter.get_lists_of_correct_occurrence()]
    assert  all(['doggo' not in l and 'fancy_man' not in l and 'extra fancy man' not in l for l in returned])


def test_styles():
    budget = 450
    roles = []
    for _ in range(10):
        encounter = Encounter(xp_budget=budget,
                                monster_source=mock_monster_list,
                                respect_roles=True,
                                occurrence='common',
                                style='leader')
        roles.append([monster['role'] for monster in encounter.monsters])
    assert all(['leader' in role_set for role_set in roles])
    roles = []
    for _ in range(10):
        encounter = Encounter(xp_budget=budget,
                                monster_source=mock_monster_list,
                                respect_roles=True,
                                occurrence='common',
                                style='elite')
        roles.append([monster['role'] for monster in encounter.monsters])
    assert all(['elite' in role_set for role_set in roles])
    roles = []
    for _ in range(10):
        encounter = Encounter(xp_budget=budget,
                                monster_source=mock_monster_list,
                                respect_roles=True,
                                occurrence='common',
                                style='basic')
        roles.append([monster['role'] for monster in encounter.monsters])
    assert all(['elite' not in role_set for role_set in roles]) and all(['leader' not in role_set for role_set in roles])

def test_encounter_source_displays_nicely():
    random_state = Random(0)
    source = EncounterSource(xp_budget=450, monster_source=MockMonsterManual, random_state=random_state)
    encounter = source.get_encounter()
    assert encounter == {'success': True,
                         'monster_set': 'mock',
                         'monsters': [
                             {'name': 'doggo', 'number': 1},
                             {'name': 'fancy man', 'number': 1}
                             ],
                         'difficulty': 0.8,
                         'xp_value': 250}


def test_encounter_source_is_deterministic():
    monsters = []
    random_state = Random(3)
    for _ in range(0, 5):
        source = EncounterSource(xp_budget=450, monster_source=MockMonsterManual, random_state=random_state)
        encounter = source.get_encounter()
        monsters.append(encounter['monsters'])
    random_state = Random(3)
    monsters2 = []
    for _ in range(0, 5):
        source = EncounterSource(xp_budget=450, monster_source=MockMonsterManual, random_state=random_state)
        encounter = source.get_encounter()
        monsters2.append(encounter['monsters'])
    assert monsters == monsters2

def test_encounters_fail_nicely():
    budget = 400000
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list)
    assert encounter.monsters == []
    budget = 0
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list)
    assert encounter.monsters == []

def test_encounter_source_fails_nicely():
    source = EncounterSource(xp_budget=0, monster_source=MockMonsterManual)
    encounter = source.get_encounter()
    assert not encounter['success']

def test_empty_lists():
    budget = 450
    encounter = Encounter(xp_budget=budget, monster_source=mock_monster_list_2, style='elite')
    # print([m['Name'] for m in encounter.monsters])
    assert encounter.monsters == []

def test_look_at_some_encounters():
    source = EncounterSource(xp_budget=900, monster_set='hobgoblins')
    encounter = source.get_encounter()
    print(encounter)
