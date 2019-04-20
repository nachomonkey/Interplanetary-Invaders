import random

from ii_game.scripts.missions import Mission, AlienPattern
from ii_game.scripts.aliens import Alien
from ii_game.scripts.names import SINGLE_NAMES

TEXTS = [
"""A group of bullies led by %s
are assulting a small space ant.
Defend the ant and destroy all
of the bullies."""]

def convertRate(rate, x):
    return (rate[0] * x, rate[1] * x)

def getNewContract(planet):
    level = random.choice(["Easy", "Medium", "Hard"])
    if level == "Easy":
        amount = 25
        rate = (.4, 1)
    if level == "Medium":
        amount = 50
        rate = (.3, .6)
    if level == "Hard":
        amount = 100
        rate = (.2, .4)
    rate = convertRate(rate, planet.alienType.difficulty)
    amount //= planet.alienType.difficulty
    mission = ContractMission()
    mission.item_types = planet.itemType
    mission.aliens = amount
    mission.patterns = [AlienPattern(rate=rate, amount=amount, aliens=[planet.alienType])]
    mission.briefing = random.choice(TEXTS) % random.choice(SINGLE_NAMES)
    return mission

class ContractMission(Mission):
    def __init__(self):
        super().__init__()
        briefing = random.choice(SINGLE_NAMES)
        items = 3
