from .dungeon_templates import DungeonTemplate
from encounters.encounter_api import EncounterSource
from treasure.npc_items import NPC_item
from string import Template
import networkx as nx
import yaml

with open('data/special_events.yaml', 'r') as f:
    special_events_data = yaml.load(f)

class SpecialEvent(DungeonTemplate):
    def distance_to_entrances(self, node, entrances, layout):
        distances = []
        for entrance in entrances:
            try:
                distance = nx.shortest_path_length(layout, node, entrance, weight='weight')
            except(nx.exception.NetworkXNoPath):
                distance = 100
            distances.append(distance)
        return min(distances)

    def room_distances(self, layout, max_edge_weight=4):
        entrances = [node for node, data in layout.nodes(data=True) if 'entrance' in data['tags']]
        navigable_paths = [(start, end) for start, end, data in layout.edges(data=True) if data['weight'] <= max_edge_weight]
        navigable_dungeon = layout.edge_subgraph(navigable_paths)
        distances = {node: self.distance_to_entrances(node, entrances, navigable_dungeon) for node in navigable_dungeon.nodes() if node not in entrances}
        return distances

    def delete_encounter(self, encounter):
        self.dungeon_manager.delete_encounter(encounter)

    def get_treasure(self, shares=1):
        return self.dungeon_manager.get_treasure(shares)

    def delete_treasure(self, treasure):
        self.dungeon_manager.delete_treasure(treasure)

    def find_best_room(self, layout):
        distances = self.room_distances(layout, max_edge_weight=4)
        sort_key = lambda x: distances[x] if distances.get(x) else 0
        distances = sorted(layout.nodes(), key=sort_key, reverse=True)
        if len(distances) > 0:
            return distances[0]
        else:
            return None


class VillainHideout(SpecialEvent):
    def get_villain(self):
        encounter_source = EncounterSource(encounter_level=self.level+1,
                                            monster_sets=['villains'],
                                            random_state=self.random_state)
        encounter_source.monster_set = self.villain_name()
        self.dungeon_manager.add_encounter_source(self.name, encounter_source)
        if self.random_state.randint(1, 6) >= 3:
            style = 'basic'
        else:
            style = 'not just pets'
        encounter = self.dungeon_manager.get_encounter(self.name, style=style)
        if encounter['difficulty'] in ['easy', 'medium'] and self.random_state.randint(1, 6) >= 3:
            item = NPC_item(self.level, random_state=self.random_state)
            encounter['treasure']['magic_items'] = item.item
        return encounter

    def find_best_room(self, layout):
        distances = self.room_distances(layout, max_edge_weight=3)
        empty_rooms = [node for node, data in layout.nodes(data=True) if data.get('encounter') is None and node in distances.keys() and 'uninhabitable' not in data['tags']]
        remaining_rooms = [node for node, data in layout.nodes(data=True) if data.get('encounter') is not None and node in distances.keys() and 'uninhabitable' not in data['tags']]
        sort_key = lambda x: distances[x] if distances.get(x) else 100
        empty_rooms = sorted(empty_rooms, key=sort_key, reverse=True)
        remaining_rooms = sorted(remaining_rooms, key=sort_key, reverse=True)
        ranked_rooms = empty_rooms + remaining_rooms
        if len(ranked_rooms) > 0:
            return ranked_rooms[0]
        else:
            return None

    def clear_room(self, node, layout):
        if layout.node[node].get('encounter') is not None:
            self.delete_encounter(layout.node[node].get('encounter'))
            layout.node[node]['encounter'] = None
        if layout.node[node].get('treasure') is not None:
            self.delete_treasure(layout.node[node].get('treasure'))
            layout.node[node]['treasure'] = None
        layout.node[node]['sign'] = None

    def populate_room(self, node, layout):
        layout.node[node]['encounter'] = self.get_villain()
        layout.node[node]['treasure'] = self.get_treasure(shares=3)

    def event_type(self):
        return 'The hideout for a well-known villain'

    def villain_name(self):
        if not hasattr(self, 'set_name'):
            self.set_name = self.dungeon_manager.name_generator.villain_name()
        return self.set_name

    def alter_dungeon(self, layout):
        best_room = self.find_best_room(layout)
        if best_room is not None:
            self.clear_room(best_room, layout)
            self.populate_room(best_room, layout)
            self.dungeon_manager.add_event(self.name, self.event_type(), self.villain_name())

class LostItem(SpecialEvent):
    def get_item(self):
        return NPC_item(self.level, martial=True, random_state=self.random_state)

    def description(self, item):
        return '\n'.join([item.name, item.item] + item.properties)

    def find_best_room(self, layout):
        distances = self.room_distances(layout, max_edge_weight=4)
        sort_key = lambda x: distances[x] if distances.get(x) else 0
        distances = sorted(layout.nodes(), key=sort_key, reverse=True)
        if len(distances) > 0:
            return distances[0]
        else:
            return None

    def event_type(self):
        return 'The last known location of a powerful magic item'

    def alter_dungeon(self, layout):
        best_room = self.find_best_room(layout)
        item = self.get_item()
        if best_room is not None:
            layout.node[best_room]['description'] += self.description(item)
            self.dungeon_manager.add_event('special', self.event_type(), item.name)

class SpecialRoom(SpecialEvent):
    def add_room(self,
                 layout,
                 secret=False,
                 passage_description=None,
                 room_description=None,
                 room_encounter=None):
        best_room = self.find_best_room(layout)
        new_room_id = len(layout.nodes())
        layout.add_room(new_room_id)
        layout.connect_rooms(best_room, new_room_id)
        layout.node[new_room_id]['description'] = room_description
        layout.node[new_room_id]['encounter'] = room_encounter
        layout.node[new_room_id]['distance'] = layout.node[best_room]['distance'] + 1
        if secret:
            layout[best_room][new_room_id]['tags'].append('secret')
            layout[best_room][new_room_id]['weight'] = 3
        else:
            layout[best_room][new_room_id]['weight'] = 1
        layout[best_room][new_room_id]['description'] = passage_description

class Prison(SpecialRoom):
    def get_encounter(self, prisoner):
        response = {}
        response['success'] = True
        response['monster_set'] = prisoner
        response['monsters'] = [{'name': prisoner, 'number': 1}]
        response['difficulty'] = None
        response['xp_value'] = None
        response['treasure'] = None
        return response

    def alter_dungeon(self, layout):
        prisoner = self.prisoner()
        self.add_room(layout,
                    secret=False,
                    room_description=self.room_description(prisoner),
                    passage_description='This passageway is barred by an enormous and imposing door - see the adjoining room description for details.',
                    room_encounter=self.get_encounter(prisoner))
        self.dungeon_manager.add_event('special', self.event_type(), prisoner)
        
    def event_type(self):
        return 'A prison for a powerful immortal being'

    def prisoner(self):
        prisoners = special_events_data['prison']['prisoners']
        return self.random_state.choice(prisoners)

    def room_description(self, prisoner):
        template = Template(self.random_state.choice(special_events_data['prison']['templates']))
        method = Template(self.random_state.choice(special_events_data['prison']['methods']))
        d = {
            'prisoner': prisoner,
            'adjective': self.random_state.choice(special_events_data['prison']['adjectives']),
            'material': self.random_state.choice(special_events_data['prison']['materials']),
            'method': method.substitute({'creature': self.prisoner()}),
            'gratitude': self.random_state.choice(special_events_data['prison']['gratitudes'])
        }
        return template.substitute(d)
        




