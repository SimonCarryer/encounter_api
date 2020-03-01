import yaml
from string import Template
from random import Random
from copy import deepcopy

class Option():
    def __init__(self, text, tags):
        self.text = text
        self.tags = tags
        self.random_state = Random()

    def add_tags(self, tags):
        for tag in self.tags:
            tags[tag] = self.random_state.choice(self.tags[tag])
        return tags

    def tags_match(self, tags):
        return all([self.tags.get(k) is None or v in self.tags.get(k) for k, v in tags.items()])

    def __repr__(self):
        return self.text

class MadLib():
    def __init__(self):
        self.random_state = Random()
        self.terms = {}

    def register_terms(self, terms):
        for term in terms:
            if terms[term].__class__ == dict:
                self.register_term(term, [(k, v) for k, v in terms[term].items()])
            elif terms[term].__class__ == list:
                self.register_term(term, [(i, {}) for i in terms[term]])

    def register_term(self, term, options):
        self.terms[term] = [Option(text, tags) for text, tags in options]
        self.terms[term[0].upper() + term[1:]] =  [Option(text[0].upper() + text[1:], tags) for text, tags in options]

    def make_d(self, tags):
        d = {}
        for t in self.terms:
            options = [option for option in self.terms[t] if option.tags_match(tags)]
            # print(t, tags, options)
            option = self.random_state.choice(options)
            tags = option.add_tags(tags)
            d[t] = option.text
        return d

    def resolve_term(self, term, **tags):
        while '$' in term:
            term = Template(term).substitute(self.make_d(tags))
        return term

if __name__ == '__main__':
    lib = MadLib()
    with open('names.yaml', 'r') as f:
        names = yaml.load(f)
    lib.register_terms(names)
    print(lib.resolve_term('$Full_name'))

