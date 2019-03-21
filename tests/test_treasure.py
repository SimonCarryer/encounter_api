from treasure.hoard import Hoard
from treasure.individual import Individual
from treasure.npc_items import NPC_item
from treasure.treasure_api import TreasureSource, HoardSource, IndividualSource
from random import Random

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
    assert hoard.items == ['Wand of the war mage, + 1']

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
    individual = Individual(1, random_state=state)
    assert individual.coins == ['13 SP']
    state = Random(0)
    individual = Individual(5, random_state=state)
    assert individual.coins == ['210 SP', '70 GP']
    state = Random(0)
    individual = Individual(11, random_state=state)
    assert individual.coins == ['500 GP', '30 PP']

def test_npc_items_returns_item():
    state = Random(0)
    item = NPC_item(1, random_state=state)
    assert item.item == 'None'
    item = NPC_item(8, random_state=state)
    assert item.item == 'Necklace of adaptation'

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
    assert sorted(treasure['items']) == ['Potion of animal friendship', 'Potion of growth', 'Potion of water breathing', 'Spell scroll (3rd leve l)']
    assert sorted(treasure['coins']) == ['1,900 GP', '130 PP', '7,000 SP', '700 CP']

def test_individual_api():
    state = Random(0)
    source = IndividualSource(encounter_level=10, random_state=state)
    treasure = source.get_treasure()
    assert sorted(treasure['coins']) == ['210 SP', '70 GP']

