from .encounter_api import EncounterSource
from utils.library import monster_manual

class Sign:
    def __init__(self, sign):
        self.sign = sign

    def __str__(self):
        return repr(self.sign)

    def delete(self):
        self.sign = None

class EncounterManager:
    def __init__(self):
        self.encounter_sources = {}
        self.encounters = {}
        self.signs = {}

    def add_encounter_source(self, source_name, encounter_source):
        self.encounter_sources[source_name] = encounter_source
        self.encounters[source_name] = 0
        self.signs[source_name] = []

    def get_encounter(self, source_name, **kwargs):
        self.encounters[source_name] += 1
        encounter = self.encounter_sources[source_name].get_encounter(**kwargs)
        encounter['source name'] = source_name
        return encounter

    def delete_encounter(self, encounter):
        source_name = encounter.get('source name')
        self.encounters[source_name] -= 1

    def get_sign(self, source_name):
        sign = Sign(self.encounter_sources[source_name].get_sign())
        self.signs[source_name].append(sign)
        return sign

    def delete_signs(self, source_name):
        for sign in self.signs[source_name]:
            sign.delete()

    def __enter__(self, *args):
        return self

    def __exit__(self, eType, eValue, eTrace):
        for source_name in self.encounter_sources:
            if self.encounters[source_name] == 0:
                self.delete_signs(source_name)
        

        

