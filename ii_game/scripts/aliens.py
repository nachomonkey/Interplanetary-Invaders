import random
import pygame
from pygame.math import Vector2

from ii_game.scripts.utils import fixPath
from ii_game.scripts.gameobject import GameObject
from ii_game.scripts.game import Bomb
from ii_game.scripts.sound import Sound

pygame.init()

G = 9.81
METER = 0.006

class Alien:
    difficulty = 1
    def __init__(self, pos, images, flaks, GOs, player, mission):
        self.GOs = GOs
        self.flaks = flaks
        self.images = images
        self.pos = list(pos)
        self.phase = 1
        self.phase_rate = .5
        self.phase_time = 0
        self.next_fire = -1
        self.fire_time = 0
        self.time_passed = 0
        self.speed = random.uniform(475, 600)
        self.downshift = 100
        self.direction = 1      # Direction 1 is right, direction -1 is left
        self.health = 1
        self.dead = False
        self.kill = False
        self.maxPhase = 9
        self.velocity = Vector2([self.speed, 0])
        self.grounded = False
        self.player = player
        self.jackpot = False
        self.hitBy = None
        self.mission = mission
        self.firesLaser = False
        self.min_drop = -.01
        self.till_reg_drop = (self.min_drop, 2)
        self.till_drop = (.05, .4)
        self.acc = 1.2
        self.drop_from = "LR"
        self.name = "alien"
        self.exp_names = ["exp", "Exp"]
        self.attack_range = (0, 30)
        self.size, self.exp_size = (64, 64), (256, 256)
        self.death_amount = [30, 15, 50, 75]
        self.life_bar = False
        self.start_health = self.health
        self.death_sound = Sound(fixPath("audio/alienDie.wav"))
        self.explode_sound = Sound(fixPath("audio/alienExplode.wav"))
        self.drop_sound = Sound(fixPath("audio/alienDrop1.wav"))
        self.impact_damage = [.2, .4]
        self.drops_bombs = False
        self.isBoss = False
        self.drops_mines = False

    def drop(self):
        if self.dead:
            return
        num = 30
        if not random.randint(0, 3):
            num = random.randint(*self.attack_range)
        num = num // 2
        Num = int(num)
        if not self.drops_bombs and not self.drops_mines and not self.firesLaser:
            Type = "rock"
        if self.drops_bombs:
            Type = "bomb"
        if self.drops_mines:
            Type = "mine"
        if self.firesLaser:
            Type = "laser"
        if Num == 0 or Num == 4:
            Type = "heart"
        if Num == 1:
            Type = "moneyBag"
        if Num == 2:
            Type = "shield"
        if num == 3 and not self.mission.items_dropped == self.mission.items:
            Type = "block"
            self.mission.items_dropped += 1
        rect = self.get_rect()
        pos = random.randint(rect.left, rect.right)
        if self.drop_from == "center":
            pos = rect.centerx
        if Type != "bomb":
            self.GOs.append(GameObject((pos, rect.centery), self.images, self.mission, Type))
        else:
            self.flaks.append(Bomb(self.images, (pos, rect.centery), self.mission))
        if type(self.till_reg_drop) in (type(3), type(3.5)):
            self.next_fire = self.till_reg_drop
        else:
            self.next_fire = random.uniform(*self.till_reg_drop)
        self.fire_time = 0
        self.drop_sound.play()

    def get_rect(self):
        rect = pygame.Rect((0, 0), self.size)
        rect.topleft = self.pos
        return rect

    def draw(self, surf):
        if not self.dead:
            surf.blit(pygame.transform.scale(self.images[f"{self.name}{self.phase}"], self.size), self.pos)
        if self.dead == 2 and not self.grounded:
            direction = "Right" if self.direction == 1 else "Left"
            surf.blit(pygame.transform.scale(self.images[f"{self.name}Falling{direction}"], self.size), self.pos)
        if self.dead == 1 or (self.dead == 2 and self.grounded):
            rect = self.get_rect()
            rect2 = pygame.Rect((0, 0), self.exp_size)
            rect2.center = rect.center
            exp_type = self.exp_names[0]
            if self.dead == 2:
                exp_type = self.exp_names[1]
            if self.phase > self.maxPhase:
                self.kill = True
                return
            surf.blit(pygame.transform.scale(self.images[f"{exp_type}{self.phase}"], self.exp_size), rect2)
        if self.life_bar:
            rect = self.get_rect()
            rect1 = pygame.Rect((0, 0), (50, 3))
            rect1.center = rect.midbottom
            rect2 = rect1.copy()
            if self.health < 0:
                self.health = 0
            rect2.w *= self.health / self.start_health
            pygame.draw.rect(surf, (0, 0, 0), rect1)
            pygame.draw.rect(surf, (0, 255, 0), rect2)

    def update(self, time_passed):
        if self.next_fire < 0:
            rect = self.get_rect()
            center = rect.center
            rect.w *= self.acc
            rect.h = 600
            rect.midtop = center
            if rect.contains(self.player.get_rect()):
                if type(self.till_drop) in (type(3), type(3.5)):
                    self.next_fire = self.till_drop
                else:
                    self.next_fire = random.uniform(*self.till_drop)
        self.time_passed = time_passed
        self.fire_time += time_passed
        self.phase_time += time_passed
        if self.fire_time >= self.next_fire and self.next_fire >= 0:
            self.drop()
        if self.dead:
            if self.dead == 1:
                self.phase_rate = .025
                self.velocity.x, self.velocity.y = [0, 0]
            if self.dead == 2:
                self.velocity[1] += (self.mission.planet.gravity * G) * time_passed / METER
        if self.phase_time >= self.phase_rate and not (self.dead == 2 and not self.grounded):
            self.phase += 1
            self.phase_time = 0
            if self.jackpot:
                self.GOs.append(GameObject((self.get_rect().x + self.get_rect().width / self.phase, self.get_rect().centery), self.images, self.mission, type = "moneyBag", amount = random.choice([50, 100])))
        if self.phase == 4 and not self.dead:
            self.phase = 1
        if self.phase == self.maxPhase:
            self.kill = True
        if self.dead == 2 and not self.grounded:
            if self.get_rect().bottom >= self.mission.ground:
                self.grounded = True
                self.velocity.x, self.velocity.y = [0, 0]
                self.phase = 1
        self.pos[0] += self.velocity[0] * self.direction * self.time_passed
        self.pos[1] += self.velocity[1] * self.time_passed
        if self.get_rect().left <= 0 and self.direction == -1:
            self.direction = 1
            self.pos[1] += self.downshift
        if self.get_rect().right >= 800 and self.direction == 1:
            self.direction = -1
            self.pos[1] += self.downshift
            
class MicroAlien(Alien):
    difficulty = .5
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.size, self.exp_size = (32, 32), (64, 64)
        self.impact_damage = [.1, .2]
        self.downshift = 32
        self.acc = 2

class PurpleAlien(Alien):       # Carpet Bomber Alien
    difficulty = 1.5
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.name = "purpleAlien"
        self.death_amount = [65, 50, 25, 100]
        self.till_drop = .05
        self.till_reg_drop = -1
        self.drop_from = "center"
        self.speed = random.uniform(200, 400)
        self.velocity = Vector2([self.speed, 0])
        self.acc = 2
        self.attack_range = (0, 100)
        self.life_bar = True
        self.health = 2
        self.start_health = 2
        self.exp_names = ["exp", "pExp"]
        self.impact_damage = [.5, 1]

class MicroAlienMK2(PurpleAlien):
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.size, self.exp_size = (32, 32), (64, 64)
        self.impact_damage = [.1, .2]
        self.downshift = 32
        self.acc = 3

class YellowAlien(Alien):   #Explosive-Bomb dropping alien (for Venus)
    difficulty = 6
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.name = "yellowAlien"
        self.death_amount = [250, 100, 150, 250]
        self.speed = random.uniform(150, 400)
        self.velocity = Vector2([self.speed, 0])
        self.drop_from = "center"
        self.till_drop = .01
        self.till_reg_drop = 4
        self.acc = 2
        self.drops_bombs = True
        self.health = 5        # Lots of armor!
        self.start_health = 5
        self.maxPhase = 15
        self.exp_names = ["yellowAlienBoomSimple"] * 2
        self.impact_damage = [1, 1]

class GreenAlien(Alien):  # Mine dropping alien (for Mercury)
    difficulty = 4
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.name = "greenAlien"
        self.death_amount = [125, 75, 75, 125]
        self.speed = random.uniform(200, 450)
        self.velocity = Vector2([self.speed, 0])
        self.drop_from = "center"
        self.till_drop = .5
        self.till_reg_drop = 2
        self.acc = 4
        self.drops_mines = True
        self.health = 2
        self.start_health = 2
        self.maxPhase = 15
        self.exp_names = ["green_boom", "green_boom_simple"]
        self.impact_damage = [.5, 1]
        self.death_sound = Sound(fixPath("audio/alienDie2.wav"))
        self.explode_sound = Sound(fixPath("audio/alienExplode2.wav"))

class VenusAlien(Alien):  # Medium-armor venus alien
    difficulty = 2
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.name = "venus_alien"
        self.death_amount = [70, 50, 75, 75]
        self.till_reg_drop = (0, 1.5)
        self.till_drop = (0.01, .05) # accurate
        self.health = 2
        self.start_health = 2
        self.maxPhase = 15
        self.exp_names = ["venus_alien_boom", "venus_alien_boom_simple"]
        self.impact_damage = [.35, .7]

class FastAlien(Alien):
    difficulty = 3
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.name = "fast_alien"
        self.death_amount = [10, 20, 30, 50]
        self.health = .5
        self.start_health = .5
        self.maxPhase = 15
        self.exp_names = ["fast_alien_boom", "fast_alien_boom_simple"]
        self.size, self.exp_size = (32, 32), (64, 64)
        self.speed = random.uniform(750, 850)
        self.velocity = Vector2([self.speed, 0])
        self.till_drop = (0.01, 1)
        self.till_reg_drop = (.1, .5)
        self.acc = 6

class JupiterAlien(Alien):
    difficulty = 1.5
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.name = "jupiter_alien"
        self.maxPhase = 15
        self.till_drop = (0, 0)
        self.health = 1.5
        self.start_health = 1.5
        self.acc = 1
        self.till_reg_drop = (0, 4)
        self.exp_names = ["jupiter_alien_boom", "jupiter_alien_boom_simple"]
        self.firesLaser = True
        self.death_sound = Sound(fixPath("audio/alienDie3.wav"))
        self.explode_sound = Sound(fixPath("audio/alienExplode3.wav"))
        self.drop_sound = Sound(fixPath("audio/alienLaser.wav"))
