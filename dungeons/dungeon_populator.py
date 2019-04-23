from random import Random
from encounters.encounter_api import EncounterSource
from treasure.treasure_api import HoardSource
from traps.trap import Trap
import networkx as nx

class NoEncountersSource:
    def get_encounter(*args, **kwargs):
        return None

class NoTrapSource:
    def get_trap(*args, **kwargs):
        return None

class NoTreasureSource:
    def get_treasure(*args, **kwargs):
        return None


class DungeonPopulator:
    def __init__(self,
                 encounter_source=None,
                 treasure_source=None,
                 trap_source=None,
                 random_state=None,
                 ):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        if encounter_source is None:
            self.encounter_source = NoEncountersSource()
        else:
            self.encounter_source = encounter_source
        if treasure_source is None:
            self.treasure_source = NoTreasureSource()
        else:
            self.treasure_source = treasure_source
        if trap_source is None:
            self.trap_source = NoTrapSource()
        else:
            self.trap_source = trap_source

    def roll(self, n):
        return self.random_state.randint(1, 6) >= n

    def sign(self):
        return self.encounter_source.get_sign()

    def get_trap(self, challenge=None):
        if self.trap_source is not None:
            return self.trap_source.get_trap(challenge=challenge)
        else:
            return None

    def monster_set(self):
        if hasattr(self.encounter_source, 'monster_set'):
            return self.encounter_source.monster_set
        else:
            return

    def add_event(self, layout):
        event = '%s: %s' % (type(self).__name__, self.monster_set())
        layout.history.append(event)

        
class OriginalInhabitants(DungeonPopulator):
    def populate(self, layout):
        for room_id, data in layout.nodes(data=True):
            trap, encounter, treasure = self.populate_room(room_id, data)
            data['trap'] = trap
            data['encounter'] = encounter
            data['treasure'] = treasure
            if trap is not None:
                data['tags'] += ['hazard', 'uninhabitable']
        self.add_event(layout)
        return layout

    def populate_room(self, room_id, data):
        trap = None
        encounter = None
        treasure = None
        if data.get('treasure') is not None:
                self.treasure_source.delete_treasure(data['treasure'])
        if 'trap' in data['tags'] and 'important' in data['tags']:
            trap = self.get_trap(challenge='deadly')
        elif 'trap' in data['tags']:
            trap = self.get_trap()
        elif 'important' in data['tags']:
            encounter = self.encounter_source.get_encounter(style='leader', difficulty='hard')
            if self.roll(5):
                treasure = self.treasure_source.get_treasure(shares=2)
        elif 'entrance' in data['tags'] and self.roll(4):
            encounter = self.encounter_source.get_encounter(style='basic')
        elif 'secret' in data['tags'] and self.roll(2):
            encounter = self.encounter_source.get_encounter(style='elite')
        elif 'guarded' in data['tags'] and self.roll(2) and self.roll(4):
            encounter = self.encounter_source.get_encounter(style='no leader', difficulty='medium')
        if 'treasure' in data['tags']:
            treasure = self.treasure_source.get_treasure()
        return trap, encounter, treasure


class UndergroundNatives(DungeonPopulator):
    def accessible_rooms(self, layout):
        accessible_rooms = []
        for node, data in layout.nodes(data=True):
            if 'cave-entrance' in data['tags'] and data.get('encounter') is None:
                accessible_rooms.append(node)
                passages = layout[node]
                for adjacent_node, data in passages.items():
                    if data['weight'] <= 3 and self.roll(3):
                        accessible_rooms.append(adjacent_node)
        return accessible_rooms

    def populate(self, layout):
        accessible_rooms = self.accessible_rooms(layout)
        for node, data in layout.nodes(data=True):
            if node in accessible_rooms:
                if 'cave-entrance' in data['tags'] and self.roll(2):
                    data['encounter'] = self.encounter_source.get_encounter(style='leader', difficulty='hard')
                    data['tags'] += ['uninhabitable']
                elif self.roll(4):
                    data['encounter'] = self.encounter_source.get_encounter()
                else:
                    data['encounter'] = None
        self.add_event(layout)
        return layout

class Lair(DungeonPopulator):
    def start_node(self, layout):
        possibles = [node for node, data in layout.nodes(data=True) if 'entrance' in data['tags'] and 'uninhabitable' not in data['tags']]
        if len(possibles) > 0:
            return self.random_state.choice(possibles)
        else:
            return None

    def populate(self, layout):
        node = self.start_node(layout)
        if node is not None:
            layout.node[node]['encounter'] = self.encounter_source.get_encounter(difficulty='hard')
            layout.node[node]['tags'] += ['hazard', 'uninhabitable']
            if layout.node[node].get('treasure') is not None:
                self.treasure_source.delete_treasure(data['treasure'])
            if self.roll(3):
                layout.node[node]['treasure'] = self.treasure_source.get_treasure(shares=2)
        self.add_event(layout)
        return layout

class Taint(DungeonPopulator):
    def populate(self, layout, tag=None):
        for node, data in layout.nodes(data=True):
            if tag in data['tags']:
                layout.node[node]['encounter'] = self.encounter_source.get_encounter()
        self.add_event(layout)
        return layout

class Explorers(DungeonPopulator):
    def start_node(self, layout):
        possibles = [node for node, data in layout.nodes(data=True) if 'entrance' in data['tags'] and 'uninhabitable' not in data['tags']]
        if len(possibles) == 0:
            return None
        return self.random_state.choice(possibles)

    def explore(self, layout, node):
        self.explored_nodes.append(node)
        passages = layout[node]
        new_nodes = []
        for adjacent_node, data in passages.items():
            if self.random_state.randint(1, 3) >= data['weight'] and adjacent_node not in self.explored_nodes and 'uninhabitable' not in layout.node[adjacent_node]['tags'] and 'hazard' not in layout.node[adjacent_node]['tags']:
                new_nodes.append(adjacent_node)
        for node in new_nodes:
            self.explore(layout, node)

    def populate(self, layout):
        start_node = self.start_node(layout)
        if start_node is None:
            return layout
        self.explored_nodes = []
        self.explore(layout, start_node)
        subgraph = layout.subgraph(self.explored_nodes)
        nodes = subgraph.nodes(data=True)
        paths = {a: len(nx.shortest_path(subgraph, start_node, a)) for a, node in nodes}
        max_path = max(paths.values())
        final_room = self.random_state.choice([key for key, value in paths.items() if value == max_path])
        for node, data in nodes:
            if data.get('treasure') is not None:
                self.treasure_source.delete_treasure(data['treasure'])
            if node == final_room:
                data['encounter'] = self.encounter_source.get_encounter(style='leader', difficulty='hard')
                if self.roll(5):
                    data['treasure'] = self.treasure_source.get_treasure(shares=2)
            elif node == start_node:
                data['encounter'] = self.encounter_source.get_encounter(style='basic')
                data['treasure'] = None
            elif self.roll(4):
                style = self.random_state.choice(['basic', 'no leader', 'no pets'])
                data['encounter'] = self.encounter_source.get_encounter(style=style)
                data['treasure'] = None
            else:
                data['encounter'] = None
                data['treasure'] = None
        self.add_event(layout)
        return layout

        



        