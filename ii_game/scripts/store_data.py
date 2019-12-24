from ii_game.scripts import items
from ii_game.scripts.vehicles import Zapper as zapper, VenusCrawler as venuscrawler, JupiterHover as jupiterhover, Curiosity as curiosity
import random
from copy import copy

ITEM_AMOUNT = (3, 10)
LISENCE_AMOUNT = (1, 4)
VEHICLE_AMOUNT = (1, 1)

class StoreItem:
    cost = 0
    title = "Example"
    type = "None"
    description = "Just an example" # Each line most be under 25 characters
    rarity = 1    # Rarity: chance of getting this item. Between 0 (never in stores) and 1 (always)
    icon = "x"
    max_mass = 0
    Onlyplanet = None
    banned_planets = []

class FireItem2x(StoreItem):
    icon = "2xfireitem"
    title = "2x Fire Rate"
    cost = 15000
    link = items.FireItem2x
    type = "Item"
    rarity = .5
    description = """
A high-value weapon which
doubles the charging rate
of the reflection chamber.
Doubles the fire rate of a
laser weapon."""

class GreenLaserItem(StoreItem):
    icon = "greenlaseritem"
    title = "Green Laser"
    link = items.GreenLaserItem
    type = "Item"
    cost = 15000
    rarity = .6
    banned_planets = ["Earth"]
    description = """
Via increasing the light
frequency in the laser
weapon, this item
quintuplicates the power
of the Red Laser"""

class DoubleMoney(StoreItem):
    icon = "2xmoney"
    title = "2x Money Multiplier"
    link = items.DoubleMoney
    type = "Item"
    cost = 5000
    rarity = .7
    description = """
For unknown scientific
reasons, this item makes
more money appear in your
wallet"""

class DoubleSpeed(StoreItem):
    icon = "2xspeed"
    title = "Double Speed"
    type = "Item"
    link = items.DoubleSpeed
    cost = 2500
    rarity = .5
    description = """
Increases the speed of
all vehicles by a factor
of two. Very helpful in
certain situations."""

class Lightning(StoreItem):
    icon = "lightning"
    title = "Lightning"
    type = "Item"
    cost = 50000
    link = items.Lightning
    rarity = .3
    banned_planets = ["Earth", "Venus", "Mars"]
    description = """
This very high-value and
expensive upgrades your
vehicle by somehow making
it launch lightning from
the cannon. The lightning
bolts fry UFOs and most
of their weapons. Power
is doubled by the Green
Laser item. For each 2x
Fire Rate item activated,
the amount of lightning 
goes up by a factor of
three"""

class FlakItem(StoreItem):
    icon = "flak"
    title = "Flak Launcher"
    type = "Item"
    cost = 30000
    rarity = .2
    link = items.FlakItem
    banned_planets = ["Earth", "Mars", "Mercury"]
    description = """
Augments your spaceship by
adding a flak launcher.
Activated by holding Left
Shift. Extremely high
damage, and high blast
radius."""

class AutoGun(StoreItem):
    icon = "autogun"
    title = "Auto Gun"
    type = "Item"
    cost = 7500
    rarity = .8
    link = items.AutoGun
    banned_planets = ["Earth", "Mars"]
    description = """
Rearranges some parts
in spaceship's firing
mechanism. Lets you hold
down the fire button
to attack constantly.
Very powerful when
combined with the 2x
Fire Rate item."""

class ShieldRegen(StoreItem):
    icon = "shield_regen"
    title = "Shield Regenerator"
    type = "Item"
    cost = 15000
    rarity = .2
    link = items.ShieldRegen
    banned_planets = ["Earth", "Venus", "Mars"]
    description = """
Adds a shield regenerator
to your vehicle for some
time."""

class MagnetItem(StoreItem):
    icon = "magnet"
    title = "Magnet"
    type = "Item"
    cost = 7000
    rarity = .3
    link = items.MagnetItem
    banned_planets = []
    description = """
This is an extremely
powerful magnet that
attracts useful objects
and repels harmful
weapons."""

class TransportLicense1(StoreItem):
    title = "Space Transport License 1"
    type = "License"
    cost = 5000
    rarity = 1
    icon = "stl1"
    max_mass = 1.5
    description = """
Base level Space
Transport License. Maximum
interplanetary travel mass
is 1.5 tons"""

class TransportLicense2(StoreItem):
    title = "SpaceTransportLicense2"
    type = "License"
    cost = 75000
    rarity = 1
    icon = "stl2"
    max_mass = 3
    description = """
Upgrades your Space
Transport License to Level
2, which allows for
interplanetary transport
of vehicles with a mass
up to 3 tons"""

class DronesLicense(StoreItem):
    title = "Drone Usage License"
    type = "License"
    cost = 50000
    rarity = .75
    icon = "drones_license"
    description = """Not Implemented"""

class ItemStorage10(StoreItem):
    title = "10 Item Storage"
    type = "License"
    cost = 50000
    rarity = .75
    icon = "10itemstorage"
    description = """
Allows you to hold
(or bring) a maximum of
10 items on your missions."""

class VenusCrawler(StoreItem):
    title = "Venus Crawler"
    type = "Vehicle"
    cost = 25000
    rarity = 1
    icon = "venus_crawler6"
    link = venuscrawler
    planet = "Earth"
    Onlyplanet = "Venus"
    description = """
The Venus Crawler is
similar to the standard
vehicle, but it is heavier
(3 tons) and can handle
temperatures up to 950
degrees F"""

class JupiterHover(StoreItem):
    title = "Jupiter Hovercraft"
    type = "Vehicle"
    cost = 45000
    rarity = 1
    icon = "jupiter_hover6"
    link = jupiterhover
    planet = "Earth"
    Onlyplanet = "Jupiter"
    description = """
This vehicle uses small
engines mounted to the
base to hover. Designed
for use on Gas Giant
planets."""

class Curiosity(StoreItem):
    title = "Curiosity Rover"
    type = "Vehicle"
    cost = 25000
    rarity = 1
    icon = "curiosity_icon"
    link = curiosity
    planet = "Earth"
    Onlyplanet = "Mars"
    description = """
NASA realized that they
could modify the laser
system on the Curiosity
rover to shoot down
aliens with a constant
beam."""

class StandardVehicle(StoreItem):
    title = "Standard Vehicle"
    type = "Vehicle"
    cost = 0
    icon = "zapper6"
    link = zapper
    description = "Standard Vehicle"

ITEMS = [GreenLaserItem, FireItem2x, DoubleMoney, DoubleSpeed, Lightning, FlakItem, AutoGun, ShieldRegen, MagnetItem] # MUST be same order and length as items.items!!!
LISENCES = [TransportLicense2, DronesLicense, ItemStorage10]
VEHICLES = [VenusCrawler, JupiterHover, Curiosity]

def getStuff(t, profile, PLANET=None):
    if PLANET == None:
        PLANET = profile["planet"].name
    if t == "items":
        AMOUNT = ITEM_AMOUNT
        LIST1 = copy(ITEMS)
    if t == "licenses":
        AMOUNT = LISENCE_AMOUNT
        LIST1 = copy(LISENCES)
    if t == "vehicles":
        AMOUNT = VEHICLE_AMOUNT
        LIST1 = copy(VEHICLES)
    LIST = copy(LIST1)
    for x in profile["inventory"]:
        for y in x:
            if y.type in ("Vehicle", "License") and y in LIST:
                LIST.remove(y)
    for x in LIST1:
        if not x in LIST:
            continue
        if x.Onlyplanet:
            if x.Onlyplanet != PLANET:
                LIST.remove(x)
                continue
        if PLANET in x.banned_planets:
            LIST.remove(x)
    items = {}
    amount = random.randint(*AMOUNT)
    picked = 0
    done = False
    if not LIST:
        return items
    while amount >= picked and not done:
        item = random.choice(LIST)
        if item.rarity >= random.uniform(0, 1) and not (item.type in ("Licence", "Vehicle") and item in items):
            picked += 1
            if not item in items:
                items[item] = 1
            else:
                items[item] += 1
        nd = False
        if item.type in ("License", "Vehicle"):
            nd = True
            for x in LIST:
                if not x in items:
                    nd = False
                else:
                    LIST.remove(x)
        done = nd
    return items
