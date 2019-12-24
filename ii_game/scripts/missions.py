from ii_game.scripts.planets import *
from ii_game.scripts.gameobject import GameObject
from ii_game.scripts.aliens import *
from ii_game.scripts import names
from ii_game.scripts import bosses
from ii_game.scripts import items
import random

class Mission:
    def __init__(self):
        self.planet = None
        self.items = 0
        self.aliens = 0
        self.bonus = 1000         # Money earned from completing the mission
        self.briefing = "Nothing"
        self.items_dropped = 0
        self.item_types = [items.DoubleMoney]
        self.friction = 1
        self.clean_room = False
        self.boss = None
        self.GOs = []
        self.images = None
        self.airport = False
        self.solar_flares = False
        self.bounce = 3
        self.temperature = 75
        self.ground = 495
        self.item_mul = 1
        self.programmed_items = {}
        self.last_aliens_killed = 0
        self.bottomless_override = None
        self.unlocks_planets = []

    def getProgTillNextItem(self, aliens_killed):
        if not self.programmed_items:
            return 0
        try:
            return (aliens_killed - self.last_aliens_killed) / (list(self.programmed_items)[0] - self.last_aliens_killed)
        except ZeroDivisionError:
            return 1

    def getItem(self):
        return random.choice(self.item_types)()

    def is_bottomless(self):
        if self.bottomless_override != None:
            return self.bottomless_override
        return self.planet.gasgiant

class MissionMercury1(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Mercury
        self.items = 3
        self.item_types = [items.ShieldRegen]
        self.programmed_items = {0 : items.ShieldRegen, 15 : items.AutoGun, 19 : items.MagnetItem}
        self.friction = 5
        self.aliens = 20
        self.bonus = 3000
        self.solar_flares = True
        self.patterns = [AlienPattern(amount = 20, rate=(.8, 4.2), aliens=[GreenAlien])]
        self.name = "Mercury Mission"
        self.backdrop = "mercury_surface"
        self.temperature = 330
        self.briefing = """On the battered surface of
the bright side of Mercury,
a group of mine-dropping alien
spiders attack.
WARNINGS: Beware of solar flares
and high temperatures"""

class MissionMercury2(MissionMercury1):
    def __init__(self):
        super().__init__()
        self.items = 3
        self.aliens = 30
        self.programmed_items = {0 : items.ShieldRegen, 10 : items.ShieldRegen, 18 : items.AutoGun, 25 : items.ShieldRegen}
        self.patterns = [AlienPattern(amount=30, rate=(.7, 3.2), aliens=[GreenAlien])]
        self.name = "More Mercury"
        self.backdrop = "mercury_surface2"
        self.bonus = 4000
        self.briefing = """You encounter more angry
enemies on your way to the
dark side of Mercury..."""

class MissionMercury3(MissionMercury1):
    def __init__(self):
        super().__init__()
        self.aliens = 75
        self.temperature = 220
        self.bonus = 5000
        self.item_types = [items.AutoGun]
        self.programmed_items = {15 : items.ShieldRegen, 20 : items.AutoGun, 35 : items.ShieldRegen, 55 : items.ShieldRegen, 65 : items.AutoGun}
        self.patterns = [AlienPattern(amount = 75, rate=(.4, 1.5), aliens=[GreenAlien, Alien, Alien])]
        self.name = "Mercury Mayhem"
        self.backdrop = "mercury_surface3"
        self.briefing = """The Mercury Spiders must have sent
out a help signal, more types of UFOs
are invading! Temperature is decreasing"""

class MissionMercury4(MissionMercury3):
    def __init__(self):
        super().__init__()
        self.aliens = 100
        self.temperature = 0
        self.bonus = 6000
        self.patterns = [AlienPattern(amount=15, rate=(.7, 3.2), aliens=[GreenAlien]),
                AlienPattern(amount=65, rate=(.3, 1.2), aliens=[Alien, Alien, Alien, GreenAlien]),
                AlienPattern(amount=5, rate=(.3, .6), aliens=[GreenAlien]),
                AlienPattern(amount=20, rate=(.2, .4), aliens=[Alien])]
        self.name = "Mercurian Madness"
        self.backdrop = "mercury_surface4"
        self.briefing = """Another wave of spiders attempts
to exterminate you from the planet."""

class MissionMercury5(MissionMercury4):
    def __init__(self):
        super().__init__()
        self.aliens = 125
        self.temperature = -150
        self.bonus = 7000
        self.programmed_items = {50 : items.AutoGun, 80 : items.MagnetItem}
        self.patterns = [AlienPattern(amount=5, rate=(.1, .4), aliens=[GreenAlien]),
                AlienPattern(amount=20, rate=(.45, .55), aliens=[Alien]),
                AlienPattern(amount=50, rate=(.75, 1.75), aliens=[Alien, GreenAlien]),
                AlienPattern(amount=50, rate=(.5, .8), aliens=[Alien, Alien, Alien, Alien, GreenAlien])]
        self.name = "The Dark Side"
        self.backdrop = "mercury_surface5"
        self.briefing = """Survive a swarm of 125 Mercurian
and other spiders."""

class MissionMercury6(MissionMercury5):
    def __init__(self):
        super().__init__()
        self.aliens = 50
        self.temperature = -175
        self.bonus = 9000
        self.programmed_items = {0 : items.ShieldRegen, 10 : items.AutoGun, 25 : items.ShieldRegen, 30 : items.AutoGun}
        self.item_types = [items.ShieldRegen]
        self.patterns = [AlienPattern(amount=3, rate=(2, 5), aliens=[MineSpreaderAlien]),
                         AlienPattern(amount=17, rate=(.2, .8), aliens=[Alien]),
                         AlienPattern(amount=15, rate=(.5, 1.5), aliens=[Alien, GreenAlien, Alien, Alien, MineSpreaderAlien]),
                         AlienPattern(amount=15, rate=(.2, 1), aliens=[Alien, GreenAlien, MineSpreaderAlien])]
        self.name = "A New Threat"
        self.briefing = """Here on the dark side of Mercury,
the Aliens have a little surprise for you."""

class MissionEarth1(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Earth
        self.boss = None
        self.items = 1
        self.item_types = [items.DoubleMoney]
        self.aliens = 25
        self.friction = 4
        self.bonus = 100
        self.patterns = [AlienPattern(amount = 25)]
        self.programmed_items = {15 : items.DoubleMoney}
        self.name = "First Mission"
        self.backdrop = "brick_with_grass"
        self.briefing = f"""Destroy a small detachment
of {self.aliens} alien spiders heading towards Earth's
surface.

WARNINGS: None"""

class MissionEarth2(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Earth
        self.boss = None
        self.items = 2
        self.item_types = [items.DoubleMoney]
        self.aliens = 40
        self.friction = 1
        self.bounce = 100
        self.bonus = 2500
        self.name = "Desert Disturbance"
        self.patterns = [AlienPattern(rate = (.2, 1.25), amount = 40)]
        self.backdrop = "earth_desert_backdrop"
        self.briefing = """A dense fleet of 40 alien spacecraft
heads towards a lonely desert.

WARNINGS: The desert sand may have low
traction with your tires"""

class MissionEarth3(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Earth
        self.boss = None
        self.item_types = [items.DoubleMoney]
        self.items = 3
        self.aliens = 75
        self.friction = 4
        self.bonus = 3000
        self.name = "Tropical Terror"
        self.patterns = [AlienPattern(rate = (.3, 2.25), amount = 20),
                AlienPattern(rate = (.2, 1.25), amount = 20),
                AlienPattern(rate = (.15, 1), amount = 35)]
        self.backdrop = "tropical_backdrop"
        self.briefing = """Destroy an invasion of 75 aliens
before they can rest on the beach

WARNINGS: None"""

class MissionEarth4(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Earth
        self.item_types = [items.FireItem2x, items.DoubleMoney]
        self.items = 2
        self.friction = -.15
        self.aliens = 100
        self.temperature = 30
        self.name = "Icy Invasion"
        self.patterns = [AlienPattern(rate = (.2, 1.5), amount = 80),
                AlienPattern(rate = (.1, .6), amount = 20)]
        self.programmed_items = {0 : items.FireItem2x, 30 : items.DoubleMoney, 75 : items.FireItem2x}
        self.bounce = 2
        self.bonus = 4000
        self.backdrop = "southpole_backdrop"
        self.briefing = """Early in the morning on the South Pole,
an army of alien spiders greets you.

WARNINGS: The icy surface provides little traction"""

class MissionEarth5(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Earth
        self.item_types = [items.DoubleSpeed]
        self.items = 1
        self.friction = 6
        self.aliens = 15
        self.name = "Clean-O-Machine-O"
        self.patterns = [AlienPattern(amount = 15, rate = (.4, 2.5))]
        self.programmed_items = {0 : items.DoubleSpeed}
        self.clean_room = True
        self.bounce = 2
        self.bonus = 5000
        self.backdrop = "clean_o_machine_o_backdrop"
        self.briefing = """15 alien spider ships have
discovered a "Clean - O - Machine - Os" electronics
factory. If even one alien crashed to the ground,
the clean room will be contaminated and you will
lose."""

class EarthAirport(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Earth
        self.item_types = [items.DoubleMoney]
        self.items = 1
        self.friction = 6
        self.aliens = 20
        self.name = "Airport Attack"
        self.patterns = [AlienPattern(amount = 20, rate = (.3, 2))]
        self.airport = True
        self.bounce = 2
        self.bonus = 5000
        self.unlocks_planets = ["Venus", "Mars"]
        self.backdrop = "city_backdrop"
        self.briefing = """Aliens spiders are beaming down
towards a city near a busy airport. Eliminate all UFOs.
After liberating the city, a spaceport will be available.

WARNINGS: Do not shoot down ANY aircraft"""

class MissionEarthBonus1(EarthAirport):
    def __init__(self):
        super().__init__()
        self.items = 3
        self.friction = 3
        self.item_types = [items.GreenLaserItem]
        self.programmed_items = {10 : items.FireItem2x, 25 : items.GreenLaserItem}
        self.aliens = 50
        self.patterns = [AlienPattern(amount=10, rate=(.01, .05)),
                AlienPattern(amount=25, rate=(.3, .75)),
                AlienPattern(amount=15, rate=(.01, .4))]
        self.name = "Lava Lake"
        self.airport = False
        self.bonus = 5000
        self.backdrop = "earth_lava_lake"
        self.temperature = 1000
        self.briefing = """Alien spiders seek refuge in
the melting-hot inferno. Eliminate them!

WARNINGS: High Temperatures"""

class MissionEarthBonus2(MissionEarth1):
    def __init__(self):
        super().__init__()
        self.aliens = 40
        self.patterns = [AlienPattern(amount=40, rate=(.2, .35), aliens=[FastAlien])]
        self.bonus = 5000
        self.name = "Destroy the Zippers"
        self.briefing = """A strange new alien spider
race has arrived on Earth. They
call themselves 'The Zippers'"""

class MissionMars1(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Mars
        self.item_types = [items.FireItem2x]
        self.items = 3
        self.friction = 1.5
        self.aliens = 30
        self.temperature = -50
        self.name = "Martian Genesis"
        self.patterns = [AlienPattern(amount = 30, rate = (.3, 2.25), aliens = [Alien, PurpleAlien])]
        self.bounce = 10
        self.bonus = 1000
        self.backdrop = "mars_backdrop1"
        self.briefing = """Welcome to Mars! The Martian spiders
have new carpet-bomber technology. Destroy a
small dose of 30 aliens.

WARNINGS: Beware of meteor showers. Low Gravity."""

class MissionMars2(MissionMars1):
    def __init__(self):
        super().__init__()
        self.aliens = 45
        self.name = "Martian Plains"
        self.item_mul = .5
        self.programmed_items = {9 : items.FireItem2x}
        self.patterns = [AlienPattern(rate=(.3, 3), amount=10, aliens=[PurpleAlien]),
                AlienPattern(rate=(.1, .4), amount=10, aliens=[Alien]),
                AlienPattern(rate=(.3, 3), amount=10, aliens=[PurpleAlien]),
                AlienPattern(rate=(.1, .4), amount=15, aliens=[Alien])]
        self.bounce = 10
        self.bonus = 2000
        self.backdrop = "mars_backdrop2"
        self.briefing = """Infuriated by your victory, alien
spiders send in even more forces."""

class MissionMars3(MissionMars1):
    def __init__(self):
        super().__init__()
        self.name = "Martian Craters"
        self.aliens = 75
        self.patterns = [AlienPattern(rate=(.1, .5), amount=5, aliens=[PurpleAlien]),
                AlienPattern(rate=(.3, 2), amount=20, aliens=[Alien]),
                AlienPattern(rate=(.2, 1.5), amount=50, aliens=[PurpleAlien, PurpleAlien, Alien])]
        self.bonus = 3500
        self.backdrop = "mars_backdrop3"
        self.briefing = """You press on towards the Martian
Spider encampments."""

class MissionMars4(MissionMars1):
    def __init__(self):
        super().__init__()
        self.name = "Martian Encampment I"
        self.aliens = 100
        self.bonus = 5000
        self.items = 2
        self.item_mul = .5
        self.patterns = [AlienPattern(rate=(.5, .6), amount = 25, aliens = [Alien]),
                AlienPattern(rate=(.4, .7), amount=50, aliens = [PurpleAlien, Alien]),
                AlienPattern(rate=(.4, .4), amount=25, aliens=[PurpleAlien, Alien])]
        self.backdrop = "mars_encampment1"
        self.briefing = """You face heavy Martian Spider opposition
as you near their homelands.

HINT: Try to find a 2x Fire Rate item."""

class MissionMars5(MissionMars1):
    def __init__(self):
        super().__init__()
        self.name = "Martian Encampment II"
        self.aliens = 100
        self.bonus = 5000
        self.items = 2
        self.item_mul = .5
        self.programmed_items = {0 : items.FireItem2x}
        self.patterns = [AlienPattern(rate=(.2, .4), amount=50, aliens=[Alien,Alien,Alien,PurpleAlien,PurpleAlien]),
                AlienPattern(rate=(.2, .35), amount=10, aliens=[Alien]),
                AlienPattern(rate=(.35, .5), amount=40, aliens=[PurpleAlien])]
        self.backdrop = "mars_encampment2"
        self.breifing = """As the Martian Encampment breaks into view,
suddenly a swarm of furious enemies assault."""

class MissionMars6(MissionMars1):
    def __init__(self):
        super().__init__()
        self.name = "NASA Zone 90235"
        self.aliens = 20
        self.programmed_items = {0 : items.FireItem2x}
        self.patterns = [AlienPattern(rate=(1, 3), amount=20, aliens=[PurpleAlien,PurpleAlien,Alien])]
        self.backdrop = "mars_cleanzone"
        self.items = 0
        self.bonus = 5000
        self.clean_room = True
        self.briefing = """NASA has targeted zone 90235
to do precise seismic data scanning. If any UFOs crash
into the ground, the seismic scanners will be damaged
and your mission will fail."""

class MissionMarsBoss(MissionMars1):
    def __init__(self):
        super().__init__()
        self.name = "Defeat The Boss"
        self.aliens = 15
        self.boss = bosses.Boss1
        self.unlocks_planets = ["Jupiter"]
        self.programmed_items = {14 : items.DoubleSpeed}
        self.patterns = [AlienPattern(rate=(.1, .3), amount=14, aliens=[Alien])]
        self.items = 0
        self.bonus = 6000
        self.briefing = f"""{names.get_name()} (a.k.a. "The Boss")
refuses to let you conquer Mars. Fight
his minions and teach him a lesson."""
        self.backdrop = "mars_backdrop3"

class MissionMarsBonus1(MissionMars1):
    def __init__(self):
        super().__init__()
        self.name = "Bomber Barage"
        self.aliens = 75
        self.programmed_items = {10 : items.FireItem2x, 50 : items.FireItem2x}
        self.patterns = [AlienPattern(rate=(.4, .8), amount=75, aliens=[PurpleAlien])]
        self.briefing = """Destroy 75 carpet bomber aliens"""
        self.backdrop = "mars_backdrop1"
        self.items = 0
        self.bonus = 5000

class MissionMarsBonus2(MissionMars1):
    def __init__(self):
        super().__init__()
        self.name = "Martian Volcanos"
        self.aliens = 75
        self.temperature = 613
        self.programmed_items = {5 : items.FlakItem, 25 : items.FireItem2x}
        self.patterns = [AlienPattern(rate=(.3, .6), amount=75, aliens=[Alien, Alien, PurpleAlien])]
        self.backdrop = "mars_volcano_backdrop"
        self.bonus = 4500
        self.briefing = """Near a massive volcano, the remaining
Martian Spiders attempt to reform to
take over Mars. Exterminate them!"""

class MissionVenus1(Mission):
    def __init__(self):
        super().__init__()
        self.planet = Venus
        self.aliens = 15
        self.name = "Venus Venture"
        self.item_types = [items.GreenLaserItem]
        self.items = 1
        self.programmed_items = {0 : items.FireItem2x, 10 : items.GreenLaserItem}
        self.patterns = [AlienPattern(rate=(.5, 3.5), amount=15, aliens=[YellowAlien])]
        self.bounce = 1
        self.friction = 3
        self.bonus = 2500
        self.temperature = 900
        self.backdrop = "venus_backdrop1"
        self.briefing = """Welcome to Venus! The Venusian
spiders have develop slow, heavy-armored spacecraft
that can drop bombs.
NOTE: First, buy the Venus Crawler vehicle
WARNINGS: Beware of volcanoes."""

class MissionVenus2(MissionVenus1):
    def __init__(self):
        super().__init__()
        self.aliens = 30
        self.name = "Up the Volcano"
        self.patterns = [AlienPattern(rate=(.2, .3), amount = 10, aliens=[VenusAlien]),
                AlienPattern(rate=(.75, 2), amount=20, aliens=[VenusAlien, YellowAlien])]
        self.bonus = 3000
        self.temperature = 950
        self.backdrop = "venus_backdrop2"
        self.briefing = """As you ascend the giant
volcano Maat Mons, different varieties
of high-armor UFOs attack.

High Temperatures"""

class MissionVenus3(MissionVenus1):
    def __init__(self):
        super().__init__()
        self.aliens = 50
        self.name = "Maat Mons"
        self.programmed_items = {0 : items.FireItem2x, 10 : items.AutoGun}
        self.patterns = [AlienPattern(rate=(.6, 1.75), amount=25, aliens=[VenusAlien, VenusAlien, YellowAlien]),
                AlienPattern(rate=(.75, 2), amount=10, aliens=[YellowAlien]),
                AlienPattern(rate=(.2, .3), amount=10, aliens=[VenusAlien]),
                AlienPattern(rate=(.5, 1.5), amount=5, aliens=[YellowAlien])]
        self.bonus = 5000
        self.temperature = 975
        self.backdrop = "venus_maatmons"
        self.briefing = """You have made it to the
top of Maat Mons. The temperatures are
very high."""
        
class MissionVenus4(MissionVenus1):
    def __init__(self):
        super().__init__()
        self.aliens = 55
        self.name = "Bombardment"
        self.patterns = [AlienPattern(rate=(.1, .3), amount=50, aliens=[VenusAlien]),
                AlienPattern(rate=(.1, .5), amount=5, aliens=[YellowAlien])]
        self.bonus = 5000
        self.backdrop = "venus_backdrop4"
        self.briefing = """Survive a quick bombardment
containing 50 medium-armor space-
ships and 5 heavy-armor ones."""

class MissionVenus5(MissionVenus1):
    def __init__(self):
        super().__init__()
        self.aliens = 15
        self.name = "Defeat the Smasher"
        self.programmed_items = {0 : items.FireItem2x, 1: items.AutoGun, 13 : items.FireItem2x, 14 : items.DoubleMoney}
        self.patterns = [AlienPattern(rate=(.1, .3), amount=10, aliens=[VenusAlien]),
                         AlienPattern(rate=(1, 2), amount=4, aliens=[YellowAlien])]
        self.bonus = 5000
        self.items = 0
        self.backdrop = "venus_backdrop4"
        self.boss = bosses.Boss2
        self.unlocks_planets = ["Mercury"]
        self.briefing = f'''Complete your conquering of
Venus by destroying {names.get_name()}, who
likes to call himself "The Smasher"'''

class MissionVenusBonus1(MissionVenus1):
    def __init__(self):
        super().__init__()
        self.aliens = 100
        self.name = "Swarms"
        self.patterns = [AlienPattern(rate=(1, 1), amount=25, aliens=[VenusAlien]),
                AlienPattern(rate=(.5, .5), amount=10, aliens=[YellowAlien]),
                AlienPattern(rate=(.75, .75), amount=25, aliens=[VenusAlien]),
                AlienPattern(rate=(.35, .35), amount=10, aliens=[YellowAlien]),
                AlienPattern(rate=(.5, .75), amount=30, aliens=[VenusAlien,YellowAlien])]
        self.bonus = 6500
        self.items = 2
        self.backdrop = "venus_backdrop5"
        self.briefing = """After hiding in a volcano,
a whole bunch of alien spiders invade."""

class MissionJupiter1(Mission):
    def __init__(self):
        super().__init__()
        self.aliens = 25
        self.planet = Jupiter
        self.name = "Jupiter Mission 1"
        self.patterns = [AlienPattern(amount=25, aliens=[JupiterAlien])]
        self.bonus = 3500
        self.items = 0
        self.ground = 600
        self.backdrop = "jupiter_backdrop1"
        self.briefing = """Welcome to Jupiter!
The alien spiders here have constructed
electric lasers. Watch out!
HINT: Press <Q> and <E> to rotate the
hover vehicle's barrel.
WARNING: You MUST have a hover vehicle"""

class MissionJupiter2(MissionJupiter1):
    def __init__(self):
        super().__init__()
        self.aliens = 40
        self.name = "Jupiter Havoc"
        self.bonus = 4500
        self.item_types = [items.FireItem2x]
        self.programmed_items = {0 : items.ShieldRegen}
        self.patterns = [AlienPattern(amount=10, rate=(.3, .55), aliens=[JupiterAlien, Alien]),
                AlienPattern(amount=20, rate=(.4, 2), aliens=[JupiterAlien, JupiterAlien, Alien]),
                AlienPattern(amount=10, rate=(.3, 1), aliens=[JupiterAlien])]
        self.items = 10
        self.backdrop = "jupiter_backdrop1"
        self.briefing = """The Earth-Spiders have
arrived to assist the Jovian
Spiders. Destroy them!"""

class MissionJupiter3(MissionJupiter1):
    def __init__(self):
        super().__init__()
        self.aliens = 125
        self.name = "Flak Time"
        self.item_types = [items.ShieldRegen]
        self.programmed_items = {0 : [items.FlakItem, items.ShieldRegen]}
        self.patterns = [AlienPattern(amount=1, rate=(3, 3), aliens=[JupiterAlien]),
                AlienPattern(amount=124, rate=(.1, .3), aliens=[JupiterAlien])]
        self.items = 20
        self.briefing = """An enormous dense wave of
UFOs is invading. Use the provided
Flak and Shield items.

HINT: Hold <Left Shift> to launch flak."""

class MissionTest(Mission):
    def __init__(self):
        super().__init__()
        self.aliens = 1
        self.planet = Earth
        self.patterns = [AlienPattern(amount=1, rate=(1000, 1000))]
        self.backdrop = "brick_with_grass"

    def getGOs(self, images):
        self.GOs = [GameObject((300, 100), images, self, "block", value = items.FlakItem)]
        return self.GOs

class AlienPattern:
    def __init__(self, rate = (.3, 2.25), amount = 100, aliens = [Alien]):
        self.rate = rate
        self.amount = amount
        self.aliens = aliens
        self.completed = 0

    def get_alien_type(self):
        return self.aliens[self.completed % len(self.aliens)]

MISSIONS = [MissionEarth1]
