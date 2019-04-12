from .dungeon import Dungeon
import random

explorers = ['bandits', 'goblins', 'orcs', 'hobgoblins', 'gnolls', 'bugbears', 'spiders', None, None]
tomb = ['tomb', 'tomb', 'spiders', 'haunted', None]
stronghold = [None, None, 'haunted']
temple = ['haunted', 'devils', 'demons', 'magical guardians', None]
treasure_vault = ['magical guardians', 'haunted', 'magical guardians']

class DungeonSource():
    def __init__(self, level):
        self.level = level
        specifications = random.choice([self.tomb(), self.stronghold(), self.temple(), self.treasure_vault()])
        self.dungeon = Dungeon(specifications)

    def get_dungeon(self):
        return self.dungeon.module()


    def tomb(self):
        specifications = {
        'inhabitants': {
            'original_inhabitants': random.choice(tomb),
            'explorers': random.choice(explorers),
            'level': self.level
            },
        'purpose': 'tomb',
        'rooms': random.randint(5, 8)
        }
        return specifications

    def mine(self):
        specifications = {
        'inhabitants': {
            'original_inhabitants': None,
            'explorers': random.choice(explorers),
            'level': self.level
            },
        'purpose': 'mine',
        'rooms': random.randint(5, 8)
        }
        return specifications
    
    def stronghold(self):
        specifications = {
        'inhabitants': {
            'original_inhabitants': random.choice(stronghold),
            'explorers': random.choice(explorers),
            'level': self.level
            },
        'purpose': 'stronghold',
        'rooms': random.randint(5, 8)
        }
        return specifications

    def temple(self):
        specifications = {
        'inhabitants': {
            'original_inhabitants': random.choice(temple),
            'explorers': random.choice(explorers),
            'level': self.level
            },
        'purpose': 'temple',
        'rooms': random.randint(5, 8)
        }
        return specifications

    def treasure_vault(self):
        specifications = {
        'inhabitants': {
            'original_inhabitants': random.choice(treasure_vault),
            'explorers': None,
            'level': self.level
            },
        'purpose': 'treasure vault',
        'rooms': random.randint(5, 8)
        }
        return specifications

