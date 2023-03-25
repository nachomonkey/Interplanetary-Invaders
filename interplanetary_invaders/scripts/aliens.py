import random
import pygame
from pygame.math import Vector2

from interplanetary_invaders.scripts.utils import fix_path, num_or_rand, clamp
from interplanetary_invaders.scripts.gameobject import GameObject
from interplanetary_invaders.scripts.game import Bomb
from interplanetary_invaders.scripts.sound import Sound

pygame.init()

G = 9.81
METER = 0.006

class Alien:
    """Base class of all aliens"""
    difficulty = 1
    item_value = (1 / 45)
    def __init__(self, pos, images, flaks, GOs, player, mission):
        self.GOs = GOs
        self.flaks = flaks
        self.images = images
        self.pos = list(pos)
        self.phase = 1
        self.phase_rate = .5
        self.death_anim_frame_rate = 0.05
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
        self.killed_by_flak = False
        self.first_grounded = False
        self.maxPhase = 9
        self.velocity = Vector2([self.speed, 0])
        self.grounded = False
        self.player = player
        self.hitBy = None
        self.mission = mission
        self.firesLaser = False
        self.min_drop = -.01
        self.till_reg_drop = (self.min_drop, 2)
        self.till_drop = (.05, .4)
        self.acc = 1.2
        self.drop_from = "LR"
        self.name = "alien"
        self.exp_names = ["alien_boom", "alien_boom_simple"]
        self.attack_range = (0, 30)
        self.size, self.exp_size = (64, 64), (256, 256)
        self.death_amount = [30, 15, 50, 75]
        self.life_bar = False
        self.start_health = self.health
        self.death_sound = Sound(fix_path("audio/alienDie.wav"))
        self.explode_sound = Sound(fix_path("audio/alienExplode.wav"))
        self.drop_sound = Sound(fix_path("audio/alienDrop1.wav"))
        self.impact_sound = None
        self.death_sound_instance = None
        self.fading = False
        self.impact_damage = [.2, .4] # Impact damage: [DAMAGE_TO_HEALTH, DAMAGE_TO_SHIELD]
        self.drops_bombs = False
        self.isBoss = False
        self.drops_mines = False
        self.explode_on_ground_impact = False
        self.spread_weapons = False
        self.num_spread = 3
        self.spread_intensity = 250
        self.post_init()
        self.hit_sound_name = "audio/alienHit.wav"
        self.hit_pitches = (.8, 1, 1.2)
#        self.dead_phase_rate = 0.025
        self.dead_phase_rate = (1 / 30)
        self.just_hurt = False

        self.drop_velocity = Vector2()

    def post_init(self):
        self.pos[0] = -self.size[0]
        self.last_health = self.health

    def play_hit_sound(self):
        if self.hit_sound_name:
            Sound(fix_path(self.hit_sound_name), pitch=random.choice(self.hit_pitches)).play()

    def drop(self, no_spread=False, horz_velocity=None, no_sound=False):
        if self.pos[0] < 0:
            return
        if self.dead:
            return
        if not no_spread and self.spread_weapons:
            AMOUNT = num_or_rand(self.num_spread) + 1
            VELOCITIES = range(-AMOUNT // 2, AMOUNT // 2)
            for e, v in enumerate(VELOCITIES):
                self.drop(True, v * self.spread_intensity, not e)
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
        if Num == 1 or Num == 5:
            Type = "moneyBag"
        if Num == 2:
            Type = "shield"
        if num == 3 and not self.mission.items_dropped == self.mission.items and not random.randint(0, 1):
            Type = "block"
            self.mission.items_dropped += 1
        rect = self.get_rect()
        pos = random.randint(rect.left, rect.right)
        vel = self.drop_velocity
        if horz_velocity:
            vel[0] = horz_velocity
        if self.drop_from == "center":
            pos = rect.centerx
        if Type != "bomb":
            self.GOs.append(GameObject((pos, rect.centery), self.images, self.mission, Type, velocity=self.drop_velocity, player=self.player))
        else:
            self.flaks.append(Bomb(self.images, (pos, rect.centery), self.mission))
        if type(self.till_reg_drop) in (type(3), type(3.5)):
            self.next_fire = self.till_reg_drop
        else:
            self.next_fire = random.uniform(*self.till_reg_drop)
        self.fire_time = 0
        if self.drop_sound and not no_sound:
            self.drop_sound.play()

    def get_rect(self):
        rect = pygame.Rect((0, 0), self.size)
        rect.topleft = self.pos
        return rect

    def draw(self, surf):
        if not self.dead:
            image = self.images[f"{self.name}{self.phase}"]
            surf.blit(pygame.transform.scale(image, self.size), self.pos)
        if self.dead == 2 and not self.grounded:
            rot = round(self.velocity.angle_to(Vector2()) * self.direction) % 360
            try:
                img = self.images[f"{self.name}Dead{rot}"]
            except KeyError:
                try:
                    img = self.images[f"{self.name}Dead"]
                except KeyError:
                    print(f"ERR: No dead image for {self.name}")
                    self.dead = 1
                    return
            scale = self.size[0] / self.images[f"{self.name}1"].get_width()
            size = Vector2(img.get_size()) * scale
            surf.blit(pygame.transform.scale(img, (round(size[0]), round(size[1]))), self.pos)
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
        if self.life_bar and not self.dead:
            rect = self.get_rect()
            rect1 = pygame.Rect((0, 0), (50, 3))
            rect1.center = rect.midbottom
            rect2 = rect1.copy()
            if self.health < 0:
                self.health = 0
            rect2.w *= self.health / self.start_health
            pygame.draw.rect(surf, (0, 0, 0), rect1)
            pygame.draw.rect(surf, (0, 255, 0), rect2)
            surf.blit(self.images["alien_bar_shading"], rect1)

    def die(self):
        self.phase_rate = self.dead_phase_rate
        self.phase = 1

    def update(self, time_passed):
        if self.just_hurt:
            self.just_hurt = False
        if self.last_health != self.health:
            self.last_health = self.health
            self.just_hurt = True
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
                self.phase_rate = self.dead_phase_rate
                self.velocity.x, self.velocity.y = [0, 0]
            if self.dead == 2:
                if not (self.grounded and self.explode_on_ground_impact):
                    self.velocity[1] += (self.mission.planet.gravity * G) * time_passed / METER
        if self.phase_time >= self.phase_rate and not (self.dead == 2 and not self.grounded):
            self.phase += 1
            self.phase_time = 0
        if self.phase == 4 and not self.dead:
            self.phase = 1
        if self.phase == self.maxPhase:
            self.kill = True
        if (self.dead == 2 and self.grounded) and self.death_sound_instance and not self.fading:
            self.death_sound_instance.fadeout(700)
            self.fading = True
        if self.dead == 2 and not self.grounded:
            if self.get_rect().bottom >= self.mission.ground:
                self.grounded = True
                if self.impact_sound:
                    self.impact_sound.play()
                self.velocity.x, self.velocity.y = [0, 0]
                self.phase = 1
                if self.explode_on_ground_impact:
                    self.explode_sound.play()
        self.pos[0] += self.velocity[0] * self.direction * self.time_passed
        self.pos[1] += self.velocity[1] * self.time_passed
        if not self.grounded and self.get_rect().left <= 0 and self.direction == -1:
            self.direction = 1
            self.pos[1] += self.downshift
        if not self.grounded and self.get_rect().right >= 800 and self.direction == 1:
            self.direction = -1
            self.pos[1] += self.downshift
            
class MicroAlien(Alien):
    """Very Small Alien"""
    difficulty = .5
    item_value = (1 / 50)
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.size, self.exp_size = (32, 32), (64, 64)
        self.impact_damage = [.1, .2]
        self.downshift = 32
        self.acc = 2
        self.post_init()

class PurpleAlien(Alien):
    """Carpet Bomber Alien"""
    difficulty = 1.5
    item_value = (1 / 25)
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
        self.exp_names = ["alien_boom", "purple_alien_boom_simple"]
        self.death_sound = Sound(fix_path("audio/purpleAlienDie.wav"))
        self.impact_damage = [.5, 1]
        self.post_init()

class MicroAlienMK2(PurpleAlien):
    """Very Small Carpet-Bomber Alien"""
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.size, self.exp_size = (32, 32), (64, 64)
        self.impact_damage = [.1, .2]
        self.downshift = 32
        self.acc = 3
        self.post_init()

class YellowAlien(Alien):
    """Bomb-dropping alien (for Venus)"""
    difficulty = 6
    item_value = (1 / 13)
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.name = "yellowAlien"
        self.death_amount = [300, 100, 150, 250]
        self.speed = random.uniform(150, 400)
        self.velocity = Vector2([self.speed, 0])
        self.drop_from = "center"
        self.till_drop = .01
        self.till_reg_drop = 4
        self.acc = 2
        self.drops_bombs = True
        self.health = 5        # Lots of armor!
        self.start_health = 5
        self.maxPhase = 14
        self.exp_names = ["yellow_boom"] * 2
        self.impact_damage = [1, 1]
        self.explode_on_ground_impact = True
        self.death_sound = Sound(fix_path("audio/yellowAlienDie.wav"))
        self.explode_sound = Sound(fix_path("audio/alienExplode2.wav"))
        self.dead_frame_rate = 0.01
        self.post_init()

class GreenAlien(Alien):
    """Mine-dropping alien (for Mercury)"""
    difficulty = 3.5
    item_value = (1 / 20)
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
        self.phase_rate = .35
        self.maxPhase = 15
        self.exp_names = ["green_boom", "green_boom_simple"]
        self.impact_damage = [.5, 1]
        self.death_sound = Sound(fix_path("audio/alienDie2.wav"))
        self.explode_sound = Sound(fix_path("audio/alienExplode2.wav"))
        self.drop_sound = Sound(fix_path("audio/alienDrop2.wav"))
        self.impact_sound = Sound(fix_path("audio/greenAlienImpact.wav"))
        self.post_init()

class MineSpreaderAlien(GreenAlien):
    """Alien that launches three mines (for Mercury)"""
    diffuculty = 4
    item_value = (1 / 15)
    def __init__(self, pos, images, flaks, GOs, player, mission):
        super().__init__(pos, images, flaks, GOs, player, mission)
        self.name = "mineSpreader"
        self.death_amount = [200, 50, 150, 150]
        self.spead = random.uniform(160, 350)
        self.velocity = Vector2([self.speed, 0])
        self.drop_from = "center"
        self.health = 3
        self.start_health = 3
        self.till_reg_drop = 3
        self.acc = 4
        self.maxPhase = 15
        self.phase_rate = .15
        self.impact_damage = [.75, 1]
        self.exp_names = ["mine_spreader_boom", "mine_spreader_boom"]
        self.explode_on_ground_impact = True
        self.spread_weapons = True
        self.spread_amount = [2, 4]
        self.drop_velocity = Vector2(0, -100)
        self.drop_sound = Sound(fix_path("audio/alienDrop3.wav"))
        self.dead_phase_rate = 0.015
        self.post_init()

class VenusAlien(Alien):
    """Medium-armor venus alien"""
    difficulty = 2
    item_value = (1 / 25)
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
        self.post_init()

class FastAlien(Alien):
    """Very Fast Alien (aka Zipper)"""
    difficulty = 3
    item_value = (1 / 20)
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
        self.post_init()

class JupiterAlien(Alien):
    """Laser-firing Alien (for Jupiter)"""
    difficulty = 1.5
    item_value = (1 / 30)
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
        self.death_sound = Sound(fix_path("audio/alienDie3.wav"))
        self.explode_sound = Sound(fix_path("audio/alienExplode3.wav"))
        self.drop_sound = Sound(fix_path("audio/alienLaser.wav"))
        self.post_init()
