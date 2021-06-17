from .encounter_api import EncounterSource


class EncounterSetSource(EncounterSource):
    def get_encounters(self):
        encounters = {}
        used_monsters = []
        used_encounters = []
        encounters["basic"] = self.basic_encounters(
            used_monsters, used_encounters)
        encounters["exotic"] = self.exotic_encounters(
            used_monsters, used_encounters)
        encounters["leader"] = self.leader_encounters(
            used_monsters, used_encounters)
        encounters["rare"] = self.rare_encounters(
            used_monsters, used_encounters)
        encounters["monster_set"] = self.monster_set.capitalize()
        return encounters

    def basic_encounters(self, used_monsters, used_encounters):
        encounters = [
            e for e in self.encounter_picker.encounters if e["style"] == "basic"]
        if len(encounters) == 0:
            return []
        final = []
        for difficulty in ["Easy", "Medium", "Hard"]:
            l = [encounter for encounter in encounters if encounter["difficulty"]
                 == difficulty and encounter["occurrence"] == "common"]
            if len(l) == 0:
                l = [encounter for encounter in encounters if encounter["difficulty"]
                     == difficulty]
            self.random_state.shuffle(l)
            final += l[:2]
        for encounter in final:
            used_monsters += encounter["monsters"]
            used_encounters.append(encounter["monster_hash"])
        return [self.format_encounter(e) for e in final]

    def exotic_encounters(self, used_monsters, used_encounters):
        encounters = [
            e for e in self.encounter_picker.encounters if e["style"] == "exotic" and e["monster_hash"] not in used_encounters]
        if len(encounters) == 0:
            return []
        final = []
        for difficulty in ["Easy", "Medium", "Hard"]:
            l = [encounter for encounter in encounters if encounter["difficulty"]
                 == difficulty and encounter["occurrence"] == "common"]
            if len(l) == 0:
                l = [encounter for encounter in encounters if encounter["difficulty"]
                     == difficulty]
            sub = []
            sub_used = []
            for e in l:
                if e["monster_hash"] not in sub_used:
                    sub.append(e)
                    sub_used.append(e["monster_hash"])
            self.random_state.shuffle(sub)
            final += sub[:2]
        for encounter in final:
            used_monsters += encounter["monsters"]
            used_encounters.append(encounter["monster_hash"])
        return [self.format_encounter(e) for e in final]

    def leader_encounters(self, used_monsters, used_encounters):
        encounters = [
            e for e in self.encounter_picker.encounters if e["style"] == "leader" and e["monster_hash"] not in used_encounters]
        if len(encounters) == 0:
            return []
        final = []
        for difficulty in ["Medium", "Hard"]:
            l = [encounter for encounter in encounters if encounter["difficulty"]
                 == difficulty and encounter["occurrence"] == "common"]
            if len(l) == 0:
                l = [encounter for encounter in encounters if encounter["difficulty"]
                     == difficulty]
            sub = []
            sub_used = []
            for e in l:
                if e["monster_hash"] not in sub_used:
                    sub.append(e)
                    sub_used.append(e["monster_hash"])
            self.random_state.shuffle(sub)
            final += sub[:3]
        for encounter in final:
            used_monsters += encounter["monsters"]
            used_encounters.append(encounter["monster_hash"])
        return [self.format_encounter(e) for e in final]

    def rare_encounters(self, used_monsters, used_encounters):
        encounters = [
            e for e in self.encounter_picker.encounters if e["monster_hash"] not in used_encounters and any(m not in used_monsters for m in e["monsters"]) and e["occurrence"] != "common"]
        if len(encounters) == 0:
            return []
        final = []
        for difficulty in ["Easy", "Medium", "Hard"]:
            l = [encounter for encounter in encounters if encounter["difficulty"]
                 == difficulty]
            sub = []
            sub_used = []
            for e in l:
                if any(m not in used_monsters for m in e["monsters"]):
                    used_monsters += e["monsters"]
                    sub_used.append(e["monster_hash"])
                    sub.append(e)
            self.random_state.shuffle(sub)
            final += sub[:2]
            if len(sub[:2]) < 2:
                sub = []
                for e in l:
                    if e["monster_hash"] not in sub_used:
                        sub.append(e)
                        sub_used.append(e["monster_hash"])
                self.random_state.shuffle(sub)
                final += sub[:2-len(sub[:2])]
        return [self.format_encounter(e) for e in final]
