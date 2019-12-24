from pygame import Vector2
from ii_game.scripts.aliens import Alien, YellowAlien

class Boss(Alien):
    def __init__(self, pos, images, GOs, flaks, player, mission):
        super().__init__(pos, images, GOs, flaks, player, mission)
        self.downshift = 0
        self.health = 10
        self.till_reg_drop = -1
        self.till_drop = .025
        self.acc = 3.5
        self.speed = 500
        self.attack_range = (30, 30)
        self.velocity = Vector2([self.speed, 0])
        self.name = "boss1"
        self.size, self.exp_size = (100, 100), (500, 500)
        self.drop_from = "center"
        self.death_amount = [3000, 2000, 500, 1000]
        self.start_health = self.health
        self.impact_damage = [1, 1]
        self.isBoss = True

class Boss1(Boss):
    pass

class Boss2(YellowAlien, Boss):
    def __init__(self, pos, images, GOs, flaks, player, mission):
        super().__init__(pos, images, GOs, flaks, player, mission)
        self.downshift = 5
        self.health = 50
        self.drops_bombs = True
        self.till_reg_drop = (-.01, .2)
        self.till_drop = (0, .5)
        self.name = "boss2"
        self.size, self.exp_size = (128, 64), (256, 256)
        self.drop_from = "LR"
        self.death_amount = [5000, 5000, 2500, 5000]
        self.start_health = self.health
        self.impact_damage = [5, 5]
