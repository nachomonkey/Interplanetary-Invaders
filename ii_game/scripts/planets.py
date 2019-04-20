#!/usr/bin/env python3

from ii_game.scripts.items import *
from ii_game.scripts.aliens import *
from ii_game.scripts.utils import remove_doubles

class Planet:
    gravity = 0             # Gravity is measured in the G (Earth's Gravity)
    name = "Planet"
    distance = 10           # Distance is measured in 10^6 miles (From the Sun). One mile is 1609.344 meters
    orbital_period = 10     # Orbital Period is measured in days
    rotational_period = 10  # Rotational Period is measured in hours (None for sync)
    surface_pressure = None # Surface pressure in atmospheres (None means Unknown)
    position = 0
    rotation = 0
    center = [0, 0]
    color = (100, 100, 100)
    isMoon = False
    moons = 0
    unlocks = []
    alienType = Alien
    itemType = DoubleMoney
    gasgiant = False
    rgba = False

class Moon(Planet):  # For moons, distance is measured in miles from its "parent"
    parent = "Planet"
    color = (100, 100, 100)
    rotational_period = None
    isMoon = True

class Mercury(Planet):
    gravity = 0.378
    name = "Mercury"
    distance = 36
    orbital_period = 88
    rotational_period = 1407.6
    color = (150, 75, 0)
    surface_pressure = 0
    unlocks = []

class Venus(Planet):
    gravity = 0.907
    name = "Venus"
    distance = 67.2
    orbital_period = 224.7
    rotational_period = -5832.5
    color = (175, 175, 45)
    surface_pressure = 91
    unlocks = ["Mercury"]
    alienType = YellowAlien
    itemType = GreenLaserItem

class Earth(Planet):
    gravity = 1
    name = "Earth"
    distance = 93
    orbital_period = 365.2
    rotational_period = 23.9
    color = (0, 200, 255)
    surface_pressure = 1
    unlocks = ["Venus", "Mars"]
    moons = 1

class EarthsMoon(Moon):
    gravity = 0.165
    parent = "Earth"
    name = "Earth's Moon"
    distance = 238855 * 1000
    orbital_period = 27.3
    rotational_period = 655.7
    unlocks = []

class Mars(Planet):
    gravity = 0.377
    name = "Mars"
    distance = 141.6
    orbital_period = 687
    rotational_period = 24.6
    color = (150, 00, 0)
    surface_pressure = 0.01
    unlocks = ["Jupiter"]
    moons = 2
    alienType = PurpleAlien
    itemType = FireItem2x

class Phobos(Moon):
    gravity = 0.055897905
    name = "Phobos"
    distance = 15092428.032 * 10
    orbital_period = 0.31891023
    color = (100, 100, 100)
    surface_pressure = None
    parent = "Mars"
    rgba = True

class Deimos(Moon):
    gravity = 0.055897905
    name = "Deimos"
    parent = "Mars"
    distance = 37753600.896 * 10
    orbital_period = 1.263
    color = (50, 50, 50)
    surface_pressure = None
    rgba = True

class Jupiter(Planet):
    gravity = 2.36
    name = "Jupiter"
    distance = 483.8
    orbital_period = 4331
    rotational_period = 9.9
    color = (255, 255, 0)
    surface_pressure = None
    unlocks = ["Saturn"]
    moons = 4
    gasgiant = True

class Io(Moon):
    name = "Io"
    parent = "Jupiter"
    gravity = 0.183
    distance = 421700000  # 421,700 km
    orbital_period = 1.769137786
    color = (57, 50, 15)
    surface_pressure = 2.9607690000000004e-15

class Europa(Moon):
    name = "Europa"
    parent = "Jupiter"
    gravity = 0.134
    distance = 670900000 # 670,900 km
    orbital_period = 3.551181
    color = (145, 145, 145)
    surface_pressure = 9.86923e-13

class Ganymede(Moon):
    name = "Ganymede"
    parent = "Jupiter"
    gravity = 0.146
    distance = 1070400000
    orbital_period = 7.15455296
    color = (50, 25, 5)
    surface_pressure = 9.86923e-07

class Callisto(Moon):
    name = "Callisto"
    parent = "Jupiter"
    gravity = 0.126
    distance = 1883000000
    orbital_period = 16.6890184
    color = (100, 100, 150)
    surface_pressure = 7.40199e-12

class Saturn(Planet):
    gravity = 0.916
    name = "Saturn"
    distance = 890.8
    orbital_period = 10474
    rotational_period = 10.7
    color = (100, 100, 20)
    surface_pressure = None
    unlocks = ["Uranus"]
    moons = 3
    gasgiant = True

class Titan(Moon):
    gravity = 0.1380695752372115
    parent = "Saturn"
    name = "Titan"
    distance = 1221870000
    orbital_period = 16
    color = (90, 75, 38)
    surface_pressure = 1.5

class Enceladus(Moon):
    gravity = 0.0113
    parent = "Saturn"
    name = "Enceladus"
    distance = 238037000
    orbital_period = 1.370218
    color = (200, 200, 200)
    surface_pressure = None

class Rhea(Moon):
    gravity = 0.02692050802261731
    parent = "Saturn"
    name = "Rhea"
    distance = 527068000
    orbital_period = 4.518212
    color = (175, 175, 175)

class Uranus(Planet):
    gravity = 0.889
    name = "Uranus"
    distance = 1784.8
    orbital_period = 30589
    rotational_period = -17.2
    color = (0, 255, 255)
    surface_pressure = None
    unlocks = ["Neptune"]

class Neptune(Planet):
    gravity = 1.12
    name = "Neptune"
    distance = 2793.1
    orbital_period = 59800
    rotational_period = 16.1
    color = (0, 100, 100)
    surface_pressure = None
    unlocks = []

class Pluto(Planet):
    gravity = 0.071
    name = "Pluto"
    distance = 3670
    orbital_period = 90560
    rotational_period = -153.3
    color = (150, 255, 255)
    surface_pressure = 0.00001

planetByName = {"Earth" : Earth,
        "Mercury" : Mercury,
        "Venus" : Venus,
        "Mars" : Mars,
        "Jupiter" : Jupiter,
        "Saturn" : Saturn,
        "Uranus" : Uranus,
        "Neptune" : Neptune,
        "Pluto" : Pluto,
        "EarthsMoon": EarthsMoon,
        "Phobos" : Phobos,
        "Deimos" : Deimos,
        "Io" : Io,
        "Europa" : Europa,
        "Ganymede" : Ganymede,
        "Callisto" : Callisto,
        "Titan" : Titan,
        "Enceladus" : Enceladus,
        "Rhea" : Rhea}

Moons = {"Mercury" : [],
        "Venus" : [],
        "Earth" : [EarthsMoon],
        "Mars" : [Phobos, Deimos],
        "Jupiter" : [Io, Europa, Ganymede, Callisto],
        "Saturn" : [Titan, Enceladus, Rhea]}

planets = [Earth, Mercury, Venus, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto]
moons = [EarthsMoon, Phobos, Deimos, Io, Europa, Ganymede, Callisto, Titan, Enceladus, Rhea]
planetsmoons = planets+moons

def unlocked_planets(profile):
    unlocked_planets = ["Earth"]
    for planet in profile["finished_planets"]:
        for p in planetsmoons:
            if p.name == planet:
                unlocked_planets.append(p.name)
                for u in p.unlocks:
                    for p2 in planetsmoons:
                        if p2.name == u:
                            unlocked_planets.append(p2.name)
    return remove_doubles(unlocked_planets)

if __name__ == "__main__":
    try:
        from ii_game.scripts import saves
    except ImportError:
        import saves
    for x in range(5):
        print(f"Unlocked Planets for profile #{x}:")
        print(self.unlocked_planets(saves.load_profile(x)))
