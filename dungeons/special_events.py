from .dungeon_templates import DungeonTemplate
from encounters.encounter_api import EncounterSource
from treasure.npc_items import NPC_item
import networkx as nx

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
        return 'villain name here'

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