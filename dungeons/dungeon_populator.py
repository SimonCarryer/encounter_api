from random import Random
from encounters.encounter_api import EncounterSource
from treasure.treasure_api import HoardSource
from traps.trap import Trap
import networkx as nx
import uuid

class NoEncountersSource:
    def get_encounter(*args, **kwargs):
        return None

    def get_sign(self, name=None):
        return None

class NoTrapSource:
    def get_trap(*args, **kwargs):
        return None

class NoTreasureSource:
    def get_treasure(*args, **kwargs):
        return None

class DungeonPopulator:
    def __init__(self,
                 name=None,
                 dungeon_manager=None,
                 trap_source=None,
                 random_state=None,
                 ):
        if name is None:
            self.name = str(uuid.uuid4())
        else:
            self.name = name
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
        if dungeon_manager is None:
            self.encounter_source = NoEncountersSource()
            self.treasure_source = NoTreasureSource()
        else:
            self.encounter_source = dungeon_manager
            self.treasure_source = dungeon_manager
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

    def get_encounter(self, **style):
        return self.encounter_source.get_encounter(self.name, **style)

    def delete_encounter(self, encounter):
        self.encounter_source.delete_encounter(encounter)

    def get_treasure(self, shares=1):
        return self.treasure_source.get_treasure(shares)

    def get_sign(self):
        return self.encounter_source.get_sign(self.name)

    def delete_treasure(self, treasure):
        self.treasure_source.delete_treasure(treasure)
  
class OriginalInhabitants(DungeonPopulator):
    def populate(self, layout):
        for room_id, data in layout.nodes(data=True):
            trap, encounter, treasure, sign = self.populate_room(room_id, data)
            data['trap'] = trap
            data['encounter'] = encounter
            data['treasure'] = treasure
            if trap is not None:
                data['tags'] += ['hazard', 'uninhabitable']
            data['sign'] = sign
        return layout

    def populate_room(self, room_id, data):
        trap = None
        encounter = None
        treasure = None
        sign = self.get_sign()
        if data.get('treasure') is not None:
            self.delete_treasure(data['treasure'])
        if data.get('encounter') is not None:
            self.delete_encounter(data['encounter'])
        if 'trap' in data['tags'] and 'important' in data['tags']:
            trap = self.get_trap(challenge='deadly')
        elif 'trap' in data['tags']:
            trap = self.get_trap()
        elif 'important' in data['tags']:
            encounter = self.get_encounter(style='leader', difficulty='hard')
            treasure = self.get_treasure(shares=2)
        elif 'entrance' in data['tags'] and self.roll(4):
            encounter = self.get_encounter(style='basic')
        elif 'secret' in data['tags'] and self.roll(2):
            encounter = self.get_encounter(style='exotic')
        elif 'guarded' in data['tags'] and self.roll(2):
            encounter = self.get_encounter(difficulty='medium')
        elif self.roll(5):
            encounter = self.get_encounter(difficulty='medium')
        if 'treasure' in data['tags'] and treasure is None:
            treasure = self.get_treasure()
        return trap, encounter, treasure, sign


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
                if data.get('encounter') is not None:
                    self.delete_encounter(data['encounter'])
                if 'cave-entrance' in data['tags']:
                    data['encounter'] = self.get_encounter()
                elif self.roll(4):
                    data['encounter'] = self.get_encounter()
                else:
                    data['encounter'] = None
                data['sign'] = self.get_sign()
        return layout

class Lair(DungeonPopulator):
    def start_node(self, layout):
        possibles = [node for node, data in layout.nodes(data=True) if 'entrance' in data['tags'] and 'uninhabitable' not in data['tags']]
        if len(possibles) > 0:
            return self.random_state.choice(possibles)
        else:
            return None

    def explore(self, layout, node):
        passages = layout[node]
        new_nodes = []
        for adjacent_node, data in passages.items():
            if self.random_state.randint(1, 2) > data['weight'] and 'uninhabitable' not in layout.node[adjacent_node]['tags'] and 'hazard' not in layout.node[adjacent_node]['tags']:
                new_nodes.append(adjacent_node)
        if len(new_nodes) > 0:
            return self.random_state.choice(new_nodes)
        else:
            return None

    def clear_room(self, node, layout):
        if layout.node[node].get('encounter') is not None:
            self.delete_encounter(layout.node[node].get('encounter'))
            layout.node[node]['encounter'] = None
        layout.node[node]['sign'] = self.get_sign()
        layout.node[node]['tags'] += ['hazard', 'uninhabitable']

    def populate(self, layout):
        node = self.start_node(layout)
        second_node = self.explore(layout, node)
        if node is not None:
            self.clear_room(node, layout)
            if second_node is not None:
                self.clear_room(second_node, layout)
                node = second_node
            layout.node[node]['encounter'] = self.get_encounter(difficulty='hard')
            if self.roll(3):
                layout.node[node]['treasure'] = self.get_treasure(shares=2)
        return layout

class Taint(DungeonPopulator):
    def populate(self, layout, tag=None):
        self.used_leader = False
        for node, data in layout.nodes(data=True):
            if tag in data['tags'] and node !=0:
                if data.get('encounter') is not None:
                    self.delete_encounter(data['encounter'])
                if 'treasure' in data['tags']: 
                    difficulty = 'hard'
                else:
                    difficulty = None
                style = self.random_state.choice(['basic', 'elite'])
                layout.node[node]['encounter'] = self.get_encounter(difficulty=difficulty, style=style)
                layout.node[node]['sign'] = ''
            elif 'important' in data['tags'] and node !=0:
                if data.get('encounter') is not None:
                    self.delete_encounter(data['encounter'])
                if 'treasure' in data['tags']: 
                    difficulty = 'hard'
                else:
                    difficulty = 'medium'  
                if self.used_leader:
                    style = 'elite'
                else:
                    style = 'leader'
                    self.used_leader = True
                layout.node[node]['encounter'] = self.get_encounter(difficulty=None, style='leader')
                layout.node[node]['sign'] = self.get_sign()           
        return layout

class Explorers(DungeonPopulator):
    def start_node(self, layout):
        possibles = [node for node, data in layout.nodes(data=True) if 'entrance' in data['tags'] and 'uninhabitable' not in data['tags']]
        if len(possibles) == 0:
            return None
        return self.random_state.choice(possibles)

    def explore(self, layout, node, iterations):
        self.explored_nodes.append(node)
        passages = layout[node]
        new_nodes = []
        for adjacent_node, data in passages.items():
            if self.random_state.randint(1, 3) >= data['weight'] and adjacent_node not in self.explored_nodes and 'uninhabitable' not in layout.node[adjacent_node]['tags'] and 'hazard' not in layout.node[adjacent_node]['tags']:
                new_nodes.append(adjacent_node)
        if iterations == 0 and len(new_nodes) == 0:
            possibles = [node for node, data in passages.items() if 'uninhabitable' not in layout.node[node]['tags']]
            if len(possibles) > 0:
                adjacent_node = self.random_state.choice(possibles)
                self.clear_passage(layout, node, adjacent_node)
                self.explore(layout, node, 1)
        for node in new_nodes:
            self.explore(layout, node, iterations + 1)

    def clear_passage(self, layout, start, end):
        passage = layout[start][end]
        passage['weight'] = 1
        passage['tags'] = [tag for tag in passage['tags'] if tag != 'secret']
        passage['description'] = 'This passage appears to have been recently cleared of debris.'

    def populate(self, layout):
        start_node = self.start_node(layout)
        if start_node is None:
            return layout
        self.explored_nodes = []
        self.explore(layout, start_node, 0)
        subgraph = layout.subgraph(self.explored_nodes)
        nodes = subgraph.nodes(data=True)
        paths = {a: len(nx.shortest_path(subgraph, start_node, a)) for a, node in nodes}
        max_path = max(paths.values())
        final_room = self.random_state.choice([key for key, value in paths.items() if value == max_path])
        for node, data in nodes:
            if data.get('encounter') is not None:
                self.delete_encounter(data['encounter'])
                data['encounter'] = None
            if data.get('treasure') is not None:
                self.delete_treasure(data['treasure'])
                data['treasure'] = None
            if node == final_room:
                data['encounter'] = self.get_encounter(style='leader', difficulty='hard')
                if self.roll(4):
                    data['treasure'] = self.get_treasure(shares=2)
                else:
                    data['treasure'] = self.get_treasure(shares=1)
            elif node == start_node:
                data['encounter'] = self.get_encounter(style='basic')
                data['treasure'] = None
            elif self.roll(4):
                data['encounter'] = self.get_encounter()
                data['treasure'] = None
            else:
                data['encounter'] = None
                data['treasure'] = None
            data['sign'] = self.get_sign()
        return layout


