from places.area import Area
from places.hazard import Hazard
#from random import Random

def test_area():
    area = Area(level=1, terrain='forest', history=['human empires'], tags=[])
    #print(area.details())

def test_hazard():
    hazard = Hazard(15, 'dangerous plants')
    #print(hazard)
