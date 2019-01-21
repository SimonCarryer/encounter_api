mock_monster_list = [
    {'Name': 'boss monster',
    'role': 'leader',
    'XP': 450,
    'occurrence': 'common'},
    {'Name': 'trooper',
    'role': 'troops',
    'XP': 100,
    'occurrence': 'common'},
    {'Name': 'fancy man',
    'role': 'elite',
    'XP': 200,
    'occurrence': 'common'},
    {'Name': 'extra fancy man',
    'role': 'elite',
    'XP': 450,
    'occurrence': 'rare'
    },
    {'Name': 'doggo',
    'role': 'pet',
    'XP': 50,
    'occurrence': 'uncommon'}
]

mock_monster_list_2 = [
    {'Name': 'nature boy',
    'role': 'natural hazard',
    'XP': 25,
    'occurrence': 'common'},
    {'Name': 'nature girl',
    'role': 'natural hazard',
    'XP': 25,
    'occurrence': 'common'},
    {'Name': 'lonely man',
    'role': 'solo',
    'XP': 50,
    'occurrence': 'common'}
]

class MockMonsterManual:
    def __init__(self):
        self.name = 'mock'
        pass

    def monsters(self, monster_set_name, random_seed):
        return mock_monster_list