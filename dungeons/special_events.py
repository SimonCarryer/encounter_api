from .dungeon_templates import DungeonTemplate
from .dungeon_populator import Explorers, Lair
from .dungeon_manager import Treasure
from encounters.encounter_api import EncounterSource
from treasure.npc_items import NPC_item
from npcs.npc import NPC
from treasure.treasure_api import RawHoardSource
from string import Template
from traps.trap import Trap
import networkx as nx
import uuid
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
    def get_encounter(self):
        encounter_source = EncounterSource(encounter_level=self.level+1,
                                            monster_sets=['villains'],
                                            random_state=self.random_state)
        encounter_source.monster_set = self.villain_name()
        self.dungeon_manager.add_encounter_source(self.name, encounter_source)
        encounter = self.dungeon_manager.get_encounter(self.name, style='leader', difficulty='medium')
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
        layout.node[node]['encounter'] = self.get_encounter()
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
        found = self.random_state.choice(special_events_data['lost item']['found'])
        base = ' ' + found + ' is "%s", a "%s" with the following special properties:\n\n' % (item.name, item.item)
        return base + '\n'.join(item.properties) + '\n'

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
                 room_encounter=None,
                 room_tags=None,
                 room_treasure=None,
                 room_link=None):
        best_room = self.find_best_room(layout)
        new_room_id = len(layout.nodes())
        layout.add_room(new_room_id)
        layout.connect_rooms(best_room, new_room_id, secret=False)
        layout.node[new_room_id]['description'] = room_description
        layout.node[new_room_id]['encounter'] = room_encounter
        layout.node[new_room_id]['treasure'] = room_treasure
        layout.node[new_room_id]['link'] = room_link
        layout.node[new_room_id]['distance'] = layout.node[best_room].get('distance', 9) + 1
        if room_tags is not None:
            layout.node[new_room_id]['tags'] += room_tags
        if secret:
            layout[best_room][new_room_id]['tags'].append('secret')
            layout[best_room][new_room_id]['weight'] = 3
        else:
            layout[best_room][new_room_id]['weight'] = 1
        layout[best_room][new_room_id]['description'] = passage_description

class ForbiddingDoor(SpecialRoom):
    def purpose(self):
        return self.random_state.choice(special_events_data['forbidding door']['purposes'])

    def get_encounter(self, prisoner):
        response = {}
        response['success'] = True
        response['monster_set'] = prisoner
        response['monsters'] = [{'name': prisoner, 'number': 1}]
        response['difficulty'] = None
        response['xp_value'] = None
        response['treasure'] = None
        return response

    def get_trap(self):
        trap = Trap(self.level, random_state=self.random_state)
        template = trap.template
        d = {
            'name': trap.name,
            'telltale': trap.telltale,
            'spot': trap.spot,
            'trigger': 'attempting to open the door',
            'damage': trap.damage,
            'save': trap.save,
            'attack': trap.attack,
            'monsters': trap.summon_monsters()
        }
        return template.substitute(d)

    def prison(self, layout):
        prisoner = self.random_state.choice(special_events_data['forbidding door']['prison']['prisoners'])
        template = Template(self.random_state.choice(special_events_data['forbidding door']['prison']['templates']))
        d = {
        'prisoner': prisoner,
        'gratitude': self.random_state.choice(special_events_data['forbidding door']['prison']['gratitudes'])
        }
        description = template.substitute(d)
        self.add_room(layout,
                    secret=False,
                    room_description=self.room_description(description),
                    passage_description='This passageway is barred by an enormous and imposing door - see the adjoining room description for details.',
                    room_encounter=self.get_encounter(prisoner))

    def treasure(self, layout):
        description = 'Behind the door is a large and richly-appointed treasure room.'
        treasure = Treasure(None)
        level = min([self.level + 5, 20])
        for item in RawHoardSource(encounter_level=level, random_state=self.random_state).get_treasure():
            treasure.get_item(*item)
        self.add_room(layout,
            secret=False,
            room_description=self.room_description(description),
            passage_description='This passageway is barred by an enormous and imposing door - see the adjoining room description for details.',
            room_encounter=None,
            room_treasure=treasure
            )

    def alter_dungeon(self, layout):
        purpose = self.purpose()
        if purpose == 'prison':
            self.prison(layout)
        elif purpose == 'treasure vault':
            self.treasure(layout)
        self.dungeon_manager.add_event('special', self.event_type(purpose), 'See below')
        
    def event_type(self, purpose):
        return special_events_data['forbidding door'][purpose]['event']

    def room_description(self, specific_description):
        template = Template(self.random_state.choice(special_events_data['forbidding door']['templates']))
        method = Template(self.random_state.choice(special_events_data['forbidding door']['methods']))
        creature = self.random_state.choice(special_events_data['forbidding door']['prison']['prisoners'])
        decoration_template = Template(self.random_state.choice(special_events_data['forbidding door']['decorations']))
        decoration_d = {}
        for word in ['script', 'message', 'motif']:
            decoration_d[word] = self.random_state.choice(special_events_data['forbidding door'][word + 's'])
        decoration = decoration_template.substitute(decoration_d)
        d = {
            'adjective': self.random_state.choice(special_events_data['forbidding door']['adjectives']),
            'material': self.random_state.choice(special_events_data['forbidding door']['materials']),
            'method': method.substitute({'creature': creature}),
            'trap': self.get_trap(),
            'decoration': decoration
        }
        return template.substitute(d) + ' ' + specific_description
        
class UnderdarkExplorers(Explorers):
    def start_node(self, layout):
        possibles = [node for node, data in layout.nodes(data=True) if 'underdark-entrance' in data.get('tags') and 'uninhabitable' not in data.get('tags')]
        if len(possibles) == 0:
            return None
        return self.random_state.choice(possibles)

class UnderdarkEntrance(SpecialRoom):
    def find_best_room(self, layout):
        free_nodes = [node for node, data in layout.nodes(data=True) if 'entrance' not in data.get('tags') and 'uninhabitable' not in data.get('tags')]
        if len(free_nodes) > 0:
            return self.random_state.choice(free_nodes)

    def room_description(self, layout):
        return self.random_state.choice(special_events_data['underdark entrance']['rooms']) + ' This room is an entrance to the underdark.'

    def passage_description(self, layout):
        if layout.purpose == 'cave':
            return ''
        else:
            return self.random_state.choice(special_events_data['underdark entrance']['passages'])

    def get_monster_sets(self):
        if self.monster_set is None:
            return self.monster_sets(required_tags=['underdark', 'dungeon-explorer']) + ['underdark']
        else:
            return [self.monster_set]

    def alter_dungeon(self, layout):
        self.add_room(layout,
                        secret=False,
                        passage_description=self.passage_description(layout),
                        room_description=self.room_description(layout),
                        room_encounter=None,
                        room_tags=['underdark-entrance'])
        monster_sets = self.get_monster_sets()
        self.build_populator(monster_sets=monster_sets, populator_method=UnderdarkExplorers).populate(layout)
        return layout

    def event_type(self):
        return 'A gateway for creatures from the underdark'


class DungeonEntrance(SpecialEvent):
    def find_best_room(self, layout):
        free_nodes = [node for node, data in layout.nodes(data=True) if 'entrance' not in data.get('tags')]
        if len(free_nodes) > 0:
            return self.random_state.choice(free_nodes)

    def room_description(self):
        return ' ' + self.random_state.choice(list(special_events_data['dungeon entrance']['entrances'])) + ' (link below)'

    def dungeon_url(self):
        guid = str(uuid.UUID(int=self.random_state.getrandbits(128)))
        level = min([self.level + self.random_state.randint(1, 3), 20])
        purpose = self.random_state.choice(list(special_events_data['dungeon entrance']['dungeon templates'].keys()))
        templates = special_events_data['dungeon entrance']['dungeon templates'][purpose]
        return '%d?guid=%s&templates=%s&terrain=%s' % (level, guid, ','.join(templates), self.dungeon_manager.terrain)

    def alter_dungeon(self, layout):
        room = self.find_best_room(layout)
        if room is not None:
            layout.node[room]['description'] += self.room_description()
            layout.node[room]['link'] = self.dungeon_url()
        return layout

class WeirdEncounter(VillainHideout):
    def get_encounter(self):
        encounter_source = EncounterSource(encounter_level=self.level+1,
                                            monster_sets=None,
                                            random_state=self.random_state)
        encounter_source.monster_set += ' - Here due to a strange alliance, a curse, or magic item.'
        self.encounter_name = encounter_source.monster_set
        self.dungeon_manager.add_encounter_source(self.name, encounter_source)
        encounter = self.dungeon_manager.get_encounter(self.name, style='elite', difficulty='hard')
        return encounter

    def event_type(self):
        return 'The site of a weird encounter'

    def alter_dungeon(self, layout):
        best_room = self.find_best_room(layout)
        if best_room is not None:
            self.clear_room(best_room, layout)
            self.populate_room(best_room, layout)
            self.dungeon_manager.add_event(self.name, self.event_type(), self.encounter_name)

class NPCHome(SpecialRoom):
    def find_best_room(self, layout):
        possibles = [node for node, data in layout.nodes(data=True) if 'entrance' in data['tags'] and 'uninhabitable' not in data['tags'] and data.get('encounter') is None]
        if len(possibles) == 0:
            possibles = [node for node, data in layout.nodes(data=True) if 'uninhabitable' not in data['tags'] and data.get('encounter') is None and data.get('sign') is None]
            if len(possibles) > 0:
                room = self.random_state.choice(possibles)
                layout.node[room]['description'] += ' A concealed door here leads to the surface.'
                layout.node[room]['tags'].append('entrance')
                return room
            else:
                return None
        else:
            return self.random_state.choice(possibles)

    def event_type(self):
        return 'The home of an eccentric ' + self.npc['role']

    def description(self):
        template = Template(self.random_state.choice(special_events_data['npc home']['template']))
        decoration = self.random_state.choice(special_events_data['npc home']['decoration'])
        furnishing = self.random_state.choice(special_events_data['npc home']['furnishing'])
        role = self.npc['role']
        pronoun_lookup = {
            'male': ('He', 'his'),
            'female': ('She', 'her'),
            'other': ('They', 'their')
        }
        pronoun, pronouns = pronoun_lookup[self.npc['sex']]
        d = {
            'decoration': decoration,
            'furnishing': furnishing,
            'role': role,
            'pronoun': pronoun,
            'pronouns': pronouns
        }
        return ' ' + template.substitute(d)

    def alter_dungeon(self, layout):
        room = self.find_best_room(layout)
        self.npc = NPC(random_state=self.random_state).details()
        if room is not None:
            layout.node[room]['npc'] = self.npc
            layout.node[room]['description'] += self.description()
            if self.random_state.randint(1, 6) >= 5:
                layout.node[room]['treasure'] = self.get_treasure(shares=1)
            self.dungeon_manager.add_event('special', self.event_type(), self.npc['name'])

class DragonLair(SpecialEvent):
    def choose_dragon(self):
        dragons = special_events_data['dragon lair']['dragons']
        print(dragons)
        dragon_source = EncounterSource(encounter_level=self.level, monster_sets=dragons)
        return dragon_source.get_encounter(difficulty='hard')

class TrapRoom(SpecialRoom):
    def make_d(self):
        d = {
            'imprecation': self.random_state.choice(special_events_data['trap room']['imprecations']),
            'material': self.random_state.choice(special_events_data['trap room']['materials']),
            'adjective': self.random_state.choice(special_events_data['trap room']['adjectives']),
            'furnishing': self.random_state.choice(special_events_data['trap room']['furnishings']),
            'motif': self.random_state.choice(special_events_data['trap room']['motifs']),
            'wall': self.random_state.choice(special_events_data['trap room']['walls']),
            'floor': self.random_state.choice(special_events_data['trap room']['floor']),
            'ceiling': self.random_state.choice(special_events_data['trap room']['ceiling']),
            'liquid_or_object': self.random_state.choice(special_events_data['trap room']['liquids'] + special_events_data['trap room']['objects']),
            'liquid_or_gas': self.random_state.choice(special_events_data['trap room']['liquids'] + special_events_data['trap room']['gasses']),
            'liquid': self.random_state.choice(special_events_data['trap room']['liquids']),
            'gas': self.random_state.choice(special_events_data['trap room']['gasses']),
            'object': self.random_state.choice(special_events_data['trap room']['objects']),
            'trigger': self.random_state.choice(special_events_data['trap room']['triggers']),
            'hazard': self.random_state.choice(special_events_data['trap room']['hazards'])
        }
        return d

    def room_description(self):
        template = Template(self.random_state.choice(special_events_data['trap room']['descriptions']))
        description = template.substitute(self.make_d())
        while '$' in description:
            description = Template(description).substitute(self.make_d())
        return description

    def add_room(self,
                 layout,
                 secret=False,
                 passage_description=None,
                 room_description=None,
                 room_encounter=None,
                 room_tags=None,
                 room_treasure=None,
                 room_link=None):
        best_room = self.find_best_room(layout)
        other_room = self.random_state.choice([i for i in range(len(layout.nodes())) if i != best_room and i != 0])
        new_room_id = len(layout.nodes())
        layout.add_room(new_room_id)
        layout.connect_rooms(best_room, new_room_id, secret=False)
        layout.connect_rooms(other_room, new_room_id, secret=False)
        layout.node[new_room_id]['description'] = room_description
        layout.node[new_room_id]['encounter'] = room_encounter
        layout.node[new_room_id]['treasure'] = room_treasure
        layout.node[new_room_id]['link'] = room_link
        layout.node[new_room_id]['distance'] = layout.node[best_room].get('distance', 9) + 1

    def alter_dungeon(self, layout):
        self.add_room(layout,
                        secret=False,
                        passage_description=None,
                        room_description=self.room_description(),
                        room_encounter=None,
                        room_tags=[])