from encounters import EncounterSource
from tests.mocks.mock_monster_list import mock_monster_list, mock_monster_list_2, MockMonsterManual
from random import Random
from encounters.encounter_builder import EncounterBuilder
from encounters.encounter_picker import EncounterPicker
from encounters.xp_calculator import XPCalulator

def test_right_role():
    budget = 450
    builder = EncounterBuilder(xp_budget=budget, monster_source=mock_monster_list)
    right_roles = [m['Name'] for m in builder.right_role([])]
    assert right_roles == ['boss monster', 'trooper', 'fancy man', 'extra fancy man', 'doggo']

def test_right_idx():
    budget = 450
    builder = EncounterBuilder(xp_budget=budget, monster_source=mock_monster_list)
    right_idx = [m['Name'] for m in builder.right_index_monsters([])]
    assert right_idx == ['boss monster', 'trooper', 'fancy man', 'extra fancy man', 'doggo']

def test_possible_monsters():
    budget = 450
    builder = EncounterBuilder(xp_budget=budget, monster_source=mock_monster_list)
    possible = [monster['Name'] for monster in builder.possible_monsters([])]
    assert possible == ['boss monster', 'trooper', 'fancy man', 'extra fancy man', 'doggo']

def test_encounter_gets_unique_combinations():
    budget = 450
    builder = EncounterBuilder(xp_budget=budget, monster_source=mock_monster_list, lower_bound=0.8, upper_bound=1.2)
    assert len(builder.monster_lists) == 9

def test_calculate_adjustment():
    calculator = XPCalulator(n_characters=4)
    adjustments = [(i, calculator.calculate_adjustment(i)) for i in range(0, 20)]
    assert adjustments == [(0, 1), (1, 1), (2, 1.5), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2.5), (8, 2.5), (9, 2.5), (10, 2.5), (11, 3), (12, 3), (13, 3), (14, 3), (15, 4), (16, 4), (17, 4), (18, 4), (19, 4)]
    calculator = XPCalulator(n_characters=2)
    adjustments = [(i, calculator.calculate_adjustment(i)) for i in range(0, 20)]
    assert adjustments == [(0, 1.5), (1, 1.5), (2, 2), (3, 2.5), (4, 2.5), (5, 2.5), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 4), (12, 4), (13, 4), (14, 4), (15, 5), (16, 5), (17, 5), (18, 5), (19, 5)]
    calculator = XPCalulator(n_characters=6)
    adjustments = [(i, calculator.calculate_adjustment(i)) for i in range(0, 20)]
    assert adjustments == [(0, 0.5), (1, 0.5), (2, 1), (3, 1.5), (4, 1.5), (5, 1.5), (6, 1.5), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2.5), (12, 2.5), (13, 2.5), (14, 2.5), (15, 3), (16, 3), (17, 3), (18, 3), (19, 3)]

def test_encounter_does_not_exceed_xp_budget():
    xp_values = []
    budget = 450
    maximum = budget * 1.5
    minimum = budget * 0.5
    source = EncounterBuilder(xp_budget=budget, monster_source=mock_monster_list)
    for monster_list in source.monster_lists:
        xp_values.append(source.xp_calulator.adjusted_xp_sum(monster_list))
    assert all([xp <= maximum for xp in xp_values])
    assert all([xp >= minimum for xp in xp_values])

def test_correct_lists_generated():
    budget = 450
    source = EncounterBuilder(xp_budget=budget, monster_source=mock_monster_list)
    correct =  [
        ['boss monster'],
        ['trooper', 'trooper', 'trooper'],
        ['doggo', 'doggo', 'trooper', 'trooper'],
        ['doggo', 'trooper', 'trooper'],
        ['trooper', 'trooper'],
        ['fancy man', 'trooper'],
        ['doggo', 'doggo', 'doggo', 'doggo', 'trooper'],
        ['doggo', 'doggo', 'doggo', 'trooper'],
        ['doggo', 'doggo', 'trooper'],
        ['fancy man', 'fancy man'],
        ['doggo', 'doggo', 'fancy man'],
        ['doggo', 'fancy man'],
        ['extra fancy man'],
        ['doggo', 'doggo', 'doggo', 'doggo', 'doggo', 'doggo'],
        ['doggo', 'doggo', 'doggo', 'doggo', 'doggo'],
        ['doggo', 'doggo', 'doggo', 'doggo'],
        ['doggo', 'doggo', 'doggo']
        ]
    returned = sorted([[m['Name'] for m in l] for l in source.monster_lists])
    assert returned == sorted(correct)

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

def test_encounter_builder_fail_nicely():
    budget = 400000
    encounter = EncounterBuilder(xp_budget=budget, monster_source=mock_monster_list)
    assert encounter.monster_lists == []
    budget = 0
    encounter = EncounterBuilder(xp_budget=budget, monster_source=mock_monster_list)
    assert encounter.monster_lists == []

def test_encounter_picker_fails_nicely():
    picker = EncounterPicker([], 450)
    encounter = picker.pick_encounter()
    assert encounter['monsters'] == []


def test_encounter_source_fails_nicely():
    source = EncounterSource(xp_budget=0, monster_source=MockMonsterManual)
    encounter = source.get_encounter()
    assert not encounter['success']

def test_look_at_some_encounters():
    source = EncounterSource(xp_budget=1000, monster_sets=None)
    encounter = source.get_encounter(difficulty=None, style=None, occurrence=None)
    # print(encounter['monsters'])

def test_encounter_builder():
    budget = 450
    monster_source = mock_monster_list
    builder = EncounterBuilder(budget, monster_source)
    assert len(builder.monster_lists) == 17
    # for m_list in builder.monster_lists:
    #     print([m['Name'] for m in m_list])

def test_encounter_picker():
    state = Random(0)
    budget = 450
    monster_source = mock_monster_list
    builder = EncounterBuilder(budget, monster_source)
    monster_lists = builder.monster_lists
    picker = EncounterPicker(monster_lists, budget, random_state=state)
    # print(picker.pick_encounter(style='no leader'))
    