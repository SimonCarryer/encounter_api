from random import Random

class Treasure(dict):
    def __init__(self, manager):
        self.manager = manager
        self.items = []
        self['coins'] = {}
        self['magic_items'] = []
        self['gemstones'] = []
        self['objects'] = []


    def get_item(self, item_type, item_value):
        self.items.append((item_type, item_value))
        if item_type == 'magic item':
            self['magic_items'].append(item_value)
        elif item_type in ['CP', 'SP', 'EP', 'GP', 'PP']:
            self['coins'][item_type] = item_value
        elif item_type == 'gem':
            self['gemstones'].append(item_value)
        else:
            self['objects'].append(item_value)
        
    def clear_items(self):
        self.items = []
        self['coins'] = {}
        self['magic_items'] = []
        self['gemstones'] = []
        self['objects'] = []


class TreasureManager:
    def __init__(self, list_of_things, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        self.list_of_things = list_of_things
        self.treasures = []
        self.shares = []

    def get_treasure(self, shares=1):
        treasure = Treasure(self)
        idx = len(self.shares)
        self.treasures.append(treasure)
        for _ in range(shares):
            self.shares.append(treasure)
        self.assign_items()
        return treasure
    
    def clear_all(self):
        for treasure in self.treasures:
            treasure.clear_items()

    def assign_items(self):
        self.clear_all()
        self.random_state.shuffle(self.shares)
        n_shares = len(self.shares)
        for idx, item in enumerate(self.list_of_things):
            self.shares[idx % n_shares].get_item(*item)

    def delete_treasure(self, treasure_to_delete):
        self.treasures = [treasure for treasure in self.treasures if treasure is not treasure_to_delete]
        self.shares = [share for share in self.shares if share is not treasure_to_delete]
        if len(self.treasures) > 0:
            self.assign_items()
