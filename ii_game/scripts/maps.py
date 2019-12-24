"""Map data for Interplanetary Invaders"""
import random
import pygame
from ii_game.scripts.planets import *
from ii_game.scripts.missions import *

MAP_POINT_SIZE = 64


class MapPoint:
    """Base class of map points"""

    def __init__(
        self,
        pos,
        name,
        mission=None,
        alien_flag=False,
        type="mission",
        will_be=None,
        next_name=None,
        bonus=False,
    ):
        self.pos = pos
        self.name = name
        self.mission = mission
        self.alien_flag = alien_flag
        self.rect = pygame.Rect((0, 0), (MAP_POINT_SIZE, MAP_POINT_SIZE))
        self.rect.midbottom = self.pos
        self.frame_time = 0
        self.max_frame = 76
        self.frame = random.randint(1, self.max_frame)
        self.frame_rate = 1 / random.randint(24, 27)
        self.type = type
        self.bonus = bonus
        self.will_be = will_be
        if next_name == None:
            next_name = name
        self.next_name = next_name
        self.old_name = self.name[:]
        self.visits_left = 3
        self.was_store = type == "store"
        self.completed = False
        self.lost = 0

    def __str__(self):
        return f"MapPoint<name={self.name}, pos={self.pos}>"

    def __repr__(self):
        return self.__str__()


AllMaps = {
    "Mercury": [
        MapPoint(
            (125, 325),
            "Mercury Mission",
            MissionMercury1,
            True,
            will_be="spaceport",
            next_name="Spaceport Mercury",
        ),
        MapPoint((300, 275), "More Mercury", MissionMercury2, True),
        MapPoint((337, 193), "Mercury Mayhem", MissionMercury3, True, will_be="store"),
        MapPoint((564, 118), "Mercurian Madness", MissionMercury4, True),
        MapPoint((725, 300), "The Dark Side", MissionMercury5, True),
        MapPoint((740, 375), "A New Threat", MissionMercury6, True),
    ],
    "Earth": [
        MapPoint((125, 100), "Landing Zone", MissionEarth1, False, type=None),
        MapPoint((300, 125), "First Mission", MissionEarth1, True),
        MapPoint((475, 60), "Desert Disturbance", MissionEarth2, True),
        MapPoint((470, 280), "Tropical Terror", MissionEarth3, True),
        MapPoint(
            (550, 380),
            "Icy Invasion",
            MissionEarth4,
            True,
            will_be="store",
            next_name="Earth Shop",
        ),
        MapPoint((675, 310), "Clean-O-Machine-O", MissionEarth5, True),
        MapPoint(
            (770, 285),
            "Airport Attack",
            EarthAirport,
            True,
            will_be="spaceport",
            next_name="Spaceport Earth",
        ),
        MapPoint((750, 345), "Lava Lake", MissionEarthBonus1, True, bonus=True),
        MapPoint(
            (610, 435), "Destroy the Zippers", MissionEarthBonus2, True, bonus=True
        ),
        #    MapPoint((0,0),"Test",None),
    ],
    "Mars": [
        MapPoint((245, 425), "Martian Genesis", MissionMars1, True),
        MapPoint(
            (480, 475),
            "Martian Plains",
            MissionMars2,
            True,
            will_be="spaceport",
            next_name="Spaceport Mars",
        ),
        MapPoint((595, 235), "Martian Craters", MissionMars3, True),
        MapPoint(
            (475, 115),
            "Martain Encampment I",
            MissionMars4,
            True,
            will_be="store",
            next_name="Mars Store",
        ),
        MapPoint((355, 100), "Martain Encampment II", MissionMars5, True),
        MapPoint((185, 100), "NASA Zone 90235", MissionMars6, True),
        MapPoint((100, 100), "Defeat The Boss", MissionMarsBoss, True),
        MapPoint((200, 300), "Bomber Barage", MissionMarsBonus1, True, bonus=True),
        MapPoint((400, 350), "Martian Volcano", MissionMarsBonus2, True, bonus=True),
    ],
    "Venus": [
        MapPoint((577, 462), "Spaceport Venus", None, type="spaceport"),
        MapPoint((378, 506), "Venus Storehouse", None, type="store"),
        MapPoint((222, 399), "Venus Venture", MissionVenus1, True),
        MapPoint((265, 245), "Up the Volcano", MissionVenus2, True),
        MapPoint((340, 255), "Maat Mons", MissionVenus3, True),
        MapPoint((485, 230), "Bombardment", MissionVenus4, True),
        MapPoint((492, 140), "Defeat the Smasher", MissionVenus5, True),
        MapPoint((363, 110), "Swarms", MissionVenusBonus1, True, bonus=True),
    ],
    "Jupiter": [
        MapPoint((73, 304), "Jupiter Hoverstation", None, type="spaceport"),
        MapPoint((132, 320), "Jovian Hoverstore", None, type="store"),
        MapPoint((200, 100), "Jupiter Mission 1", MissionJupiter1, True),
        MapPoint((300, 125), "Jupiter Havoc", MissionJupiter2, True),
        MapPoint((400, 175), "Flak Time", MissionJupiter3, True),
    ],
}

SavedPoints = {}
for x in PLANET_BY_NAME:
    SavedPoints[x] = 0
