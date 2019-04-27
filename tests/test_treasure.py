from treasure.hoard import Hoard
from treasure.individual import Individual
from treasure.npc_items import NPC_item
from treasure.treasure_api import TreasureSource, HoardSource, IndividualSource, RawHoardSource
from random import Random
from treasure.treasure_tables import item_values

def test_hoard_is_instantiated_with_level():
    hoard = Hoard(1)
    assert hoard.level == 1

def test_hoard_generates_items():
    state = Random(0)
    hoard = Hoard(1, random_state=state)
    assert hoard.items == ['Potion of climbing', 'Potion of climbing', 'Spell scroll (cantrip)']
    state = Random(5)
    hoard = Hoard(5, random_state=state)
    assert hoard.items == ['Ammunition, +3']
    state = Random(5)
    hoard = Hoard(11, random_state=state)
    assert hoard.items == ['Wand of the war mage, +1']

def test_hoard_generates_objects():
    state = Random(0)
    hoard = Hoard(1, random_state=state)
    assert hoard.objects == '5 art objects of value 25gp each (total 125gp)'

def test_hoard_generates_coins():
    state = Random(0)
    hoard = Hoard(1, random_state=state)
    assert hoard.coins == ['2,200 CP', '700 SP', '60 GP']

def test_individual_treasure_returns_coins():
    state = Random(0)
    individual = Individual(random_state=state)
    coins = individual.roll_on_table(1)
    assert coins['SP'] == 13
    state = Random(0)
    individual = Individual(random_state=state)
    coins = individual.roll_on_table(5)
    assert coins['SP'] == 210
    assert coins['GP'] == 70
    state = Random(0)
    individual = Individual(random_state=state)
    for level in [1, 5, 10]:
        individual.roll_on_table(level)
    assert individual.coins['CP'] == 1200
    assert individual.coins['EP'] == 120

def test_individual_treasure_generates_objects():
    state = Random(0)
    individual = Individual(random_state=state)
    for level in [1, 5, 10]:
        individual.roll_on_table(level)
    individual.coins_to_objects()
    #assert individual.objects == 'Gemstones and jewelry worth 330GP.'

# def test_npc_items_returns_item():
#     state = Random(0)
#     item = NPC_item(1, random_state=state)
#     assert item.item == 'None'
#     item = NPC_item(8, random_state=state)
#     assert item.item == 'Winged boots'

def test_npc_items_rarities():
    state = Random(0)
    # for level in range(1, 21):
    #     print(NPC_item(level, random_state=state).rarities())

def test_npc_items_properties():
    state = Random()
    item = NPC_item(13, random_state=state)
    # print(item.properties)
    # print(item.item)

def test_treasure_api_sets_level():
    source = TreasureSource(encounter_level=1)
    assert source.level == 1

def test_treasure_api_sets_level_from_budget():
    source = TreasureSource(xp_budget=500)
    assert source.level == 3
    source = TreasureSource(xp_budget=10001)
    assert source.level == 14

def test_treasure_api_sets_level_character_dict():
    source = TreasureSource(character_level_dict={4: 4})
    assert source.level == 4

def test_hoard_api():
    state = Random(0)
    source = HoardSource(encounter_level=10, random_state=state)
    treasure = source.get_treasure()
    assert treasure['objects'] == '8 gems of value 50gp each (total 400gp)'
    assert sorted(treasure['magic_items']) == ['Potion of animal friendship', 'Potion of growth', 'Potion of water breathing', 'Spell scroll (3rd level)']
    assert sorted(treasure['coins']) == ['1,900 GP', '130 PP', '7,000 SP', '700 CP']

def test_individual_api():
    state = Random(0)
    monsters = [{'Type': 'Humanoid', 'Challenge': 5}]
    source = IndividualSource(monsters, random_state=state)
    treasure = source.get_treasure()
    #assert treasure['coins']['GP'] == 70