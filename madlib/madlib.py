import yaml
from string import Template
from random import Random
from copy import deepcopy
import re

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

class Term():
    def __init__(self, template):
        self.template = template
        self.random_state = Random()
        self.options = []

    def select_option(self, tags):
        options = [option for option in self.options if option.tags_match(tags)]
        return self.random_state.choice(options)

    def register_option(self, text, tags):
        self.options.append(Option(text, tags))

    def __repr__(self):
        return self.template

class MadLib():
    def __init__(self):
        self.random_state = Random()
        self.terms = []
        self.article_patterns = [(r'\$A( [aeiou])', r'An\1'), (r'\$a( [aeiou])', r'an\1'), (r'\$A( [^aeiou$])', r'A\1'), (r'\$a( [^aeiou$])', r'a\1')]


    def register_terms(self, terms_dict, term_class=Term):
        for term_text in terms_dict:
            if terms_dict[term_text].__class__ == dict:
                self.register_term(term_text, [(k, v) for k, v in terms_dict[term_text].items()], term_class=term_class)
            elif terms_dict[term_text].__class__ == list:
                self.register_term(term_text, [(i, {}) for i in terms_dict[term_text]], term_class=term_class)

    def register_term(self, term_template, options, term_class=Term):
        term = term_class(term_template)
        for text, tags in options:
            term.register_option(text, tags)
        self.terms.append(term)
        term = term_class(term_template[0].upper() + term_template[1:])
        for text, tags in options:
            term.register_option(text[0].upper() + text[1:], tags)
        self.terms.append(term)        

    def make_d(self, tags):
        d = {}
        for term in self.terms:
            option = term.select_option(tags)
            tags = option.add_tags(tags)
            d[term.template] = option.text
        return d

    def resolve_term(self, term, **tags):
        while '$' in term:
            term = Template(term).safe_substitute(self.make_d(tags))
            term = self.substitute_articles(term)
        return term

    def substitute_articles(self, template_string):
        for pattern, repl in self.article_patterns:
            template_string = re.sub(pattern, repl, template_string)
        return template_string

if __name__ == '__main__':
    lib = MadLib()
    with open('names.yaml', 'r') as f:
        names = yaml.load(f)
    lib.register_terms(names)
    print(lib.resolve_term('$thing'))
