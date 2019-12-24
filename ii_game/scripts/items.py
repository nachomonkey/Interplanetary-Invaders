import time
import random

class Item:
    def __init__(self):
        self.length = 10
        self.total_time = 0
        self.activated = False
        self.name = "Item"

    def activate(self):
        self.activated = True

class GreenLaserItem(Item):
    cost = 10000
    def __init__(self):
        super().__init__()
        self.length = 25
        self.name = "Green Laser"
        self.image = "greenlaseritem"

class FireItem2x(Item):
    cost = 10000
    def __init__(self):
        super().__init__()
        self.length = 20
        self.name = "2x Fire Rate"
        self.image = "2xfireitem"

class DoubleMoney(Item):
    cost = 3500
    def __init__(self):
        super().__init__()
        self.length = 30
        self.name = "2x Money Bonus"
        self.image = "2xmoney"

class DoubleSpeed(Item):
    cost = 2500
    def __init__(self):
        super().__init__()
        self.length = 25
        self.name = "2x Speed"
        self.image = "2xspeed"

class Lightning(Item):
    cost = 50000
    def __init__(self):
        super().__init__()
        self.length = 30
        self.name = "Lightning"
        self.image = "lightning"

class FlakItem(Item):
    cost = 30000
    def __init__(self):
        super().__init__()
        self.length = 40
        self.name = "Flak Bursts"
        self.image = "flak"

class AutoGun(Item):
    cost = 4500
    def __init__(self):
        super().__init__()
        self.length = 40
        self.name = "Auto Gun"
        self.image = "autogun"

class ShieldRegen(Item):
    cost = 10000
    def __init__(self):
        super().__init__()
        self.length = 25
        self.name = "Shield Regenerator"
        self.image = "shield_regen"

class MagnetItem(Item):
    cost = 7000
    def __init__(self):
        super().__init__()
        self.length = 30
        self.name = "Magnet"
        self.image = "magnet"

items = [GreenLaserItem, FireItem2x, DoubleMoney, DoubleSpeed, Lightning, FlakItem, AutoGun, ShieldRegen, MagnetItem]

def getItem():
    return random.choice(items)()
