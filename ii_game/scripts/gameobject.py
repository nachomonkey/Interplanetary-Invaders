import pygame, random, copy
from pygame.math import Vector2
from ii_game.scripts import constants
from ii_game.scripts.utils import fixPath
from ii_game.scripts.sound import Sound

pygame.init()

G = 9.81
METER = 0.006
SIZE = (800, 600)
shared = {"money_ser_num" : 0}

class GameObject:
    def __init__(self, center, images, mission, type = "moneyBag", velocity = Vector2([0, 0]), amount = None, value = None):
        self.images = images
        self.type = type
        self.size = (24, 24)
        self.physics = True
        self.gotShot = False
        if self.type == "moneyBag":
            self.size = (12, 16)
        if self.type == "rock":
            self.size = (20, 20)
        if self.type == "aircraft":
            self.physics = False
            self.size = (48, 48)
        if self.type == "mine":
            self.size = (32, 32)
        self.rect_size = self.size
        if self.type == "laser":
            self.size = (32, 32)
            self.rect_size = (16, 32)
        rect = pygame.Rect((0, 0), self.size)
        rect.center = center
        self.pos = list(rect.topleft)
        self.rect = rect
        self.time_passed = 0
        self.frame = 1
        self.frame_rate = 1 / 25
        self.frame_time = 0
        self.max_frame = 185
        self.velocity = copy.copy(velocity)
        self.dead = False
        self.kill = False
        self.amount = amount
        self.jackpot = False
        self.mission = mission
        self.health = .1
        self.kaboom = False
        if self.type == "block":
            self.max_frame = 30
        if self.type == "moneyBag":
            self.health = 1
            self.ser_num = shared["money_ser_num"]
            shared["money_ser_num"] += 1
        if self.type == "aircraft":
            self.depart = random.randint(0, 1)
            self.direction = random.randint(0, 1)
            if self.direction == 0:
                self.direction = -1
            if self.depart == 0:
                self.depart = -1
            self.frame_rate = 1
            self.max_frame = 3
            x = 0
            y = 0
            if self.direction == -1:
                x = SIZE[0]
            if self.depart == -1:
                y = self.mission.ground
            rect = self.get_rect()
            rect.center = (x, y)
            self.pos = list(rect.topleft)
            self.velocity = Vector2([1 * self.direction, .5 * self.depart]) * 300 * random.uniform(.9, 1.1)
            self.jet_sound = Sound(fixPath("audio/jet.wav"))
            self.jet_sound.play(-1)
        if self.type == "mine":
            self.frame_rate = .5
            self.max_frame = 3
            self.health = 1
        if self.type == "laser":
            self.max_frame = 5
            self.frame_rate = 0.01
            self.physics = False
            self.velocity = Vector2([0, 1200])
        self.value = value
        self.start_health = self.health
        self.life_bar = True
        self.hitBy = []
        self.lifetime = 0
        # Bounce equation:
#        V = (V - GF) * (C + C2)

    def get_rect(self):
        """Returns a pygame.Rect object representing this GameObject"""
        rect = pygame.Rect((0, 0), self.rect_size)
        rect.topleft = self.pos
        return rect

    def draw(self, surf):
        if self.type in ("moneyBag", "rock") and not self.dead:
            surf.blit(self.images[self.type], self.pos)
        if self.type in "moneyBag" and self.dead:
            self.max_frame = 75
            rect = self.get_rect()
            rect2 = pygame.Rect((0, 0), (256, 256))
            rect2.center = rect.center
            if self.frame > self.max_frame:
                self.kill = True
                return
            surf.blit(self.images[f"money_explosion_t{(self.ser_num % 5) + 1}_{self.frame}"], rect2)
        if self.type in ("shield", "block", "heart", "mine", "laser") and not self.dead:
            t = self.type
            if t == "laser":
                t = "bluelaser"
            surf.blit(pygame.transform.scale(self.images[f"{t}{self.frame}"],
                (32, 32)), self.pos)
        if self.type == "aircraft" and not self.dead:
            surf.blit(pygame.transform.flip(pygame.transform.scale(self.images[f"aircraft{'Down' if self.depart == 1 else ''}{self.frame}"], self.size), self.direction == -1, 0), self.pos)
        if self.type in ("rock", "block", "heart", "shield") and self.dead:
            self.max_frame = 10
            if self.type in ("block", "heart", "shield"):
                self.max_frame = 29
            rect = self.get_rect()
            rect2 = pygame.Rect((0, 0), (50, 50))
            if self.type in ("block", "heart", "shield"):
                rect2 = pygame.Rect((0, 0), (96, 96))
            rect2.center = rect.center
            if self.frame > self.max_frame - 1:
                self.kill = True
                return
            if self.type in ("block", "heart", "shield"):
                t = self.type
                if t == "block":
                    t = "item"
                surf.blit(self.images[f"{t}_boom{self.frame}"], rect2)
            else:
                surf.blit(self.images[f"rockCrush{self.frame}"], rect2)
        if self.type == "aircraft" and self.dead:
            self.max_frame = 58
            rect = self.get_rect()
            rect2 = pygame.Rect((0, 0), (128, 128))
            rect2.center = rect.center
            if self.frame > 58:
                self.kill = True
                return
            surf.blit(self.images[f"aircraft_explode{self.frame}"], rect2)
        if self.type == "mine" and self.dead:
            self.max_frame = 15
            rect = self.get_rect()
            rect2 = pygame.Rect((0, 0), (128, 128))
            rect2.center = rect.center
            if self.frame > 58:
                self.kill = True
                return
            surf.blit(self.images[f"mine_boom{self.frame}"], rect2)

    def update(self, time_passed):
        self.lifetime += time_passed
        if self.type == None:
            return
        rect = self.get_rect()
        if self.type == "aircraft":
            if not pygame.Rect(0, 0, 800, 600).colliderect(rect):
                self.jet_sound.stop()
                self.kill = True
        if rect.bottom < self.mission.ground and self.physics:
            self.velocity[1] += (self.mission.planet.gravity * G) * time_passed / METER
        if rect.bottom > self.mission.ground and self.physics:
            if self.type == "rock":
                self.dead = True
                self.frame = 1
            if self.type == "laser":
                self.kill = True
            if self.type in ("block", "moneyBag", "heart", "shield") and self.mission.planet.gasgiant:
                self.dead = True
                self.frame = 1
                self.physics = False
                self.velocity[0] = 0
                self.velocity[1] = 0
                self.frame_rate = 1/30
            rect.bottom = self.mission.ground
            self.pos = list(rect.topleft)
            self.velocity[1] = -((self.velocity[1] - (self.mission.planet.gravity * G) * time_passed / METER) / (constants.BOUNCE[self.type] + self.mission.bounce))
            if round(self.velocity[1], 1) == 0:
                self.velocity[0] = 0
                self.velocity[1] = 0
        if not (self.type in ("moneyBag", "aircraft") and self.dead):
            self.pos[0] += self.velocity[0] * self.time_passed
            self.pos[1] += self.velocity[1] * self.time_passed
        self.frame_time += time_passed
        if self.frame_time >= self.frame_rate and not (self.type=="moneyBag" and not self.dead):
            self.frame += 1
            self.frame_time = 0
        if self.frame >= self.max_frame:
            if self.dead and self.type in ("rock", "moneyBag", "aircraft", "mine", "block", "shield", "heart"):
                self.kill = True
            self.frame = 1
        if self.kill:
            if self.type == "aircraft":
                self.jet_sound.stop()
        self.time_passed = time_passed
