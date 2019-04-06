big_adjustments = {k: v for k, v in [(0, 0.5), (1, 0.5), (2, 1), (3, 1.5), (4, 1.5), (5, 1.5), (6, 1.5), (7, 2), (8, 2), (9, 2), (10, 2), (11, 2.5), (12, 2.5), (13, 2.5), (14, 2.5), (15, 3), (16, 3), (17, 3), (18, 3), (19, 3), (20, 3)]}
med_adjustments = {k: v for k, v in [(0, 1), (1, 1), (2, 1.5), (3, 2), (4, 2), (5, 2), (6, 2), (7, 2.5), (8, 2.5), (9, 2.5), (10, 2.5), (11, 3), (12, 3), (13, 3), (14, 3), (15, 4), (16, 4), (17, 4), (18, 4), (19, 4), (20, 4)]}
small_adjustments = {k: v for k, v in [(0, 1.5), (1, 1.5), (2, 2), (3, 2.5), (4, 2.5), (5, 2.5), (6, 3), (7, 3), (8, 3), (9, 3), (10, 3), (11, 4), (12, 4), (13, 4), (14, 4), (15, 5), (16, 5), (17, 5), (18, 5), (19, 5), (20, 5)]}


class XPCalulator:
    def __init__(self, n_characters=4):
        if n_characters <= 2:
            self.adjustments = small_adjustments
        elif n_characters >= 6:
            self.adjustments = big_adjustments
        else:
            self.adjustments = med_adjustments
        
    def calculate_adjustment(self, n_monsters):
        return self.adjustments[n_monsters]

    def adjusted_xp_sum(self, monster_list):
        monster_count = len(monster_list)
        adjustment = self.calculate_adjustment(monster_count)
        return sum([monster['XP'] * adjustment for monster in monster_list])
