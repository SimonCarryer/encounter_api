import yaml
from string import Template
from random import Random
from copy import deepcopy

with open('data/names.yaml') as f:
    names_data = yaml.load(f)

with open('data/books.yaml') as f:
    books_data = yaml.load(f)

class NameGenerator:
    def __init__(self, random_state=None):
        if random_state is None:
            self.random_state = Random()
        else:
            self.random_state = random_state
            
    def sex(self):
        return self.random_state.choice(['male', 'female'])
    
    def simple_person_name(self, sex=None):
        if sex is None:
            sex = self.sex()
        names = names_data['personal names']['%s names' % sex] 
        return self.random_state.choice(names)

    def place(self, terrain=None):
        if terrain is None:
            terrain = self.random_state.choice(['forest', 'hills', 'mountains', 'swamp', 'arctic', 'jungle', 'plains', 'desert'])
        template = Template(self.random_state.choice(names_data['places']['templates']))
        d = {
        'simple_name': self.simple_person_name(),
        'geography': self.random_state.choice(names_data['places']['geography'][terrain]),
        'adjective': self.random_state.choice(names_data['places']['adjectives']),
        'symbol': self.random_state.choice(names_data['other words']['symbols']),
        'title': self.title(),
        'sobriquet': self.random_state.choice(names_data['personal names']['sobriquets'])
        }
        return template.substitute(d)
    
    def title(self, sex=None):
        if sex is None:
            sex = self.sex()
        titles = names_data['personal names']['%s titles' % sex] 
        return self.random_state.choice(titles)
    
    def prefix(self, sex=None):
        if sex is None:
            sex = self.sex()
        prefixes = names_data['personal names']['%s prefixes' % sex] 
        return self.random_state.choice(prefixes)
    
    def prefix_name(self, sex=None):
        if sex is None:
            sex = self.sex()
        template = Template(self.random_state.choice(names_data['personal names']['prefix templates']))
        d = {
        'name': self.simple_person_name(sex),
        'descriptor': self.random_state.choice(names_data['personal names']['descriptors']),
        'prefix': self.prefix(sex)}
        return template.substitute(d)
    
    def villain_name(self, sex=None):
        if sex is None:
            sex = self.sex()        
        template = Template(self.random_state.choice(names_data['personal names']['villain templates']))
        d = {
        'name': self.simple_person_name(sex),
        'descriptor': self.random_state.choice(names_data['personal names']['descriptors']),
        'sobriquet': self.random_state.choice(names_data['personal names']['sobriquets']),
        'prefix': self.prefix(sex)}
        return template.substitute(d)
        
    def fancy_name(self, sex=None):
        if sex is None:
            sex = self.sex()
        name_template = Template(self.random_state.choice(names_data['personal names']['fancy templates']))
        name = self.simple_person_name(sex)
        d = {
        'name': self.simple_person_name(sex),
        'descriptor': self.random_state.choice(names_data['personal names']['descriptors']),
        'prefix': self.prefix(sex),
        'title': self.title(sex),
        'adjective': self.random_state.choice(names_data['personal names']['adjectives']),
        'sobriquet': self.random_state.choice(names_data['personal names']['sobriquets'])}
        return name_template.substitute(d)
    
    def weapon(self):
        template = Template(self.random_state.choice(names_data['weapons']['templates']))
        first = self.random_state.choice(names_data['weapons']['first'])
        last = self.random_state.choice([w for w in names_data['weapons']['last'] if w != first.lower()])
        d = {
        'fancy_name': self.fancy_name(),
        'symbol': self.random_state.choice(names_data['other words']['symbols']),
        'first': first,
        'last': last,
        'weapon': self.random_state.choice(names_data['weapons']['items']),
        'sobriquet': self.random_state.choice(names_data['personal names']['sobriquets'])
        }
        return template.substitute(d)

    def shield(self):
        template = Template(self.random_state.choice(names_data['shields']['templates']))
        d = {
        'fancy_name': self.fancy_name(),
        'symbol': self.random_state.choice(names_data['other words']['symbols']),
        'shield': self.random_state.choice(names_data['shields']['items']),
        'sobriquet': self.random_state.choice(names_data['personal names']['sobriquets'])
        }
        return template.substitute(d)

    def armour(self):
        template = Template(self.random_state.choice(names_data['armour']['templates']))
        d = {
        'fancy_name': self.fancy_name(),
        'symbol': self.random_state.choice(names_data['other words']['symbols']),
        'armour': self.random_state.choice(names_data['armour']['items']),
        'sobriquet': self.random_state.choice(names_data['personal names']['sobriquets'])
        }
        return template.substitute(d)

    def settlement(self, terrain=None):
        if terrain is None:
            terrain = self.random_state.choice(['arctic', 'mountains', 'plains', 'forest', 'swamp', 'desert'])
        first = self.random_state.choice(names_data['settlement']['first'] + names_data['settlement'].get(terrain, {}).get('first', []))
        last = self.random_state.choice(names_data['settlement']['last'] + names_data['settlement'].get(terrain, {}).get('last', []))
        return first + last

    def alignment(self):
        alignment = self.random_state.choice(['Lawful', 'Neutral', 'Chaotic']) + ' ' + self.random_state.choice(['Evil', 'Neutral', 'Good'])
        if alignment == 'Neutral Neutral':
            alignment = 'True Neutral'
        return alignment

    def fancy_term(self):
        template = Template(self.random_state.choice(books_data['fancy terms']['template']))
        d = {
            'first': self.random_state.choice(books_data['fancy terms']['first']),
            'middle': self.random_state.choice(books_data['fancy terms']['middle']),
            'last': self.random_state.choice(books_data['fancy terms']['last'])
        }
        return template.substitute(d)

    def book(self, book_type=None):
        if book_type is None:
            book_type = self.random_state.choice(['arcana', 'history', 'nature', 'religion'])
        title_template = Template(self.random_state.choice(books_data['template'][book_type]['title']))
        d = {
            'name': self.simple_person_name(),
            'adjective': self.random_state.choice(books_data['template'][book_type].get('adjective', ['', ''])),
            'word': self.random_state.choice(books_data['word']),
            'person': self.random_state.choice(books_data['person']),
            'place': self.random_state.choice(books_data['place']),
            'subject': self.random_state.choice(books_data['subject']),
            'environment': self.random_state.choice(books_data['environment']),
            'fancy_name': self.fancy_name(),
            'settlement': self.settlement(),
            'fancy_term': self.fancy_term(),
            'alignment': self.alignment(),
            'creature': self.random_state.choice(books_data['creature'])
        }
        title = title_template.substitute(d)
        if self.random_state.randint(1, 6) >= 5:
            content_template = Template(self.random_state.choice(books_data['template'][book_type]['content']['rare']))
        else:
            content_template = Template(self.random_state.choice(books_data['template'][book_type]['content']['common']))
        content = content_template.substitute(d)
        if self.random_state.randint(1, 6) >= 5:
            types = ['physical', 'other']
            if book_type in ['religion', 'arcana']:
                types.append('language')
            feature_type = self.random_state.choice(types)
            extra = self.random_state.choice(books_data['features'][feature_type])
        else:
            extra = ''
        return {'title': title, 'contents': content, 'extra': extra}

    
    def dungeon_name(self, dungeon_type, terrain=None):
        template = Template(self.random_state.choice(names_data['templates'][dungeon_type]))
        d = {'simple_name': self.simple_person_name(),
             'title': self.title(),
             'prefix_name': self.prefix_name(),
             'fancy_name': self.fancy_name(),
             'settlement': self.settlement(terrain=terrain),
            'place': self.place(terrain),
             'noun': self.random_state.choice(names_data['dungeon types'][dungeon_type]['nouns']),
             'material': self.random_state.choice(names_data['other words']['materials']),
             'symbol': self.random_state.choice(names_data['other words']['symbols']),
             'adjective': self.random_state.choice(names_data['other words']['adjectives']),
             'belonging': self.random_state.choice(names_data['dungeon types'][dungeon_type]['belongings']),
             'descriptor': self.random_state.choice(names_data['personal names']['descriptors']),
             'sobriquet': self.random_state.choice(names_data['personal names']['sobriquets'])
            }
        return template.safe_substitute(d)
        