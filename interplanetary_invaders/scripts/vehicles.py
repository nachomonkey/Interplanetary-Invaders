import pygame, math
from math import radians, sin, cos
from pygame.math import Vector2
from interplanetary_invaders.scripts.lasers import *
from interplanetary_invaders.scripts.sound import Sound
from interplanetary_invaders.scripts.utils import fix_path
from interplanetary_invaders.scripts import joystick

pygame.init()

class Zapper:
    """Zapper (Player) class"""

    def __init__(self, pos, images, mission, dry = False):
        self.dry = dry
        self.pos = pos
        self.images = images
        self.speed = 1                # Acceleration multiplier
        self.acceleration = 1
        self.fire_per_sec = 4.5
        self.completeness = 1
        self.title = "Alien Zapper 1"
        self.name = "zapper"
        self.time_passed = 0
        self.lasers = []
        self.size = (64, 64)
        self.boom_size = (200, 200)
        self.rect = self.get_rect()
        self.health = 1
        self.shield = 0
        self.max_health = 1
        self.max_shield = 1
        self.hover_alt = 0
        self.min_alt = 0
        self.target_alt = 0
        self.standard_alt = 0
        self.alt_change_speed = 5
        self.hitBy = []
        self.items = []
        self.current_items = {}
        self.fireObject = Laser
        self.dead = False
        self.kill = False
        self.frame = 1
        self.frame_rate = 1 / 25
        self.frame_time = 0
        self.friction = 1
        self.velocity = pygame.Vector2((0, 0))
        self.max_velocity = 6
        self.target_x_velocity = 0
        self.mission = mission
        self.mass = 1.5           # Mass in kilograms
        self.death_frames = 25
        self.max_temp = 300 # Works up to 300 deg. F
        self.canFire = True
        self.fire_from = "center"
        self.beam = False
        self.rotation = 0
        self.rotation_speed = 90
        self.max_rotation = 60
        self.add_temp = 0
        self.rotate = False
        self.whimp = False
        self.regen = False
        self.hover = False
        self.extra_dip = 0
        self.send_to_ground()
        self.regen_time = 0
        self.just_fired = False
        self.death_sound = None
        self.weapon_power = 1
        self.always_beam = False
        self.general_acc = 20
        self.im_back = False
        self.invincible = False        
        self.invincible_time = 0
        self.even_frame = True
        self.damage_sound = Sound("audio/takeDamage.wav", True)
        self.fire_sound_pitches = (.95, 1, 1.05)

    def send_to_ground(self):
        if self.dry:
            return
        rect = self.get_rect()
        if not self.hover:
            rect.bottom = self.mission.ground
        else:
            rect.bottom = self.hover_alt
        self.standard_alt = rect.bottom
        self.target_alt = self.standard_alt
        self.min_alt = self.mission.ground
        self.pos[1] = rect.top
        if not self.hover and self.mission.is_bottomless():
            self.dead = True
            self.health = 0
            self.shield = 0
        if self.hover and self.mission.is_bottomless():
            self.min_alt += self.extra_dip

    def get_rect(self):
        """Returns a pygame.Rect object representing the player"""
        rect = pygame.Rect((0, 0), self.size)
        rect.topleft = self.pos
        return rect

    def make_invincible(self, no_sound=False):
        if self.dead:
            return
        self.invincible = True
        self.invincible_time = .75
        if not no_sound:
            self.damage_sound.play()

    def draw(self, surf):
        """Render the Zapper"""
        if not self.dead:
            if self.invincible and not self.even_frame:
                return
            if self.rotate:
                line_len = 50
                start_pos = Vector2(self.fire_from) + self.pos
                end_pos = start_pos - Vector2(cos(radians(self.rotation + 90)) * line_len, sin(radians(self.rotation + 90)) * line_len)
                pygame.draw.line(surf, (255, 0, 0), start_pos, end_pos, 1)
            name = f"{self.name}{int(6 * (self.completeness / 1))}"
            if name in self.images:
                self.image=pygame.transform.scale(self.images[name], self.size)
            if self.rotate and self.completeness == 1 or not name in self.images:
                lr = ""
                if self.rotation >= 45:
                    lr = "R"
                if self.rotation <= -45:
                    lr = "L"
                surf.blit(pygame.transform.scale(self.images[self.name + lr], self.size), self.pos)
            else:
                surf.blit(self.image, self.pos)
        if self.dead:
            rect = self.get_rect()
            rect.size = self.boom_size
            rect.center = self.get_rect().center
            surf.blit(pygame.transform.scale(self.images[f"{self.name}Die{self.frame}"], self.boom_size), rect)

    def fire(self):
        self.completeness = 0
        center = Vector2(self.get_rect().topleft)
        if self.fire_from != "center":
            center += Vector2((self.fire_from))
        else:
            center += (Vector2(self.size) / 2)
        obj = self.fireObject(center, self.images, self.rotation)
        obj.damage *= self.weapon_power
        if self.whimp:
            obj.damage /= 10
        self.lasers.append(obj)
        if not self.whimp:
            pitch = random.choice(self.fire_sound_pitches)
            obj.fire_sound.__init__(obj.fire_sound.original_filename, pitch=pitch)
            obj.fire_sound.play()
        return obj

    def events(self, event):
        """Handle user events for Zapper"""
        if (event.type == pygame.KEYDOWN or joystick.WasEvent()) and not self.dead:
            if (event.key in (pygame.K_SPACE, pygame.K_UP, pygame.K_w) or joystick.JustPressedX()) and self.completeness == 1 and self.canFire:
                obj = self.fire()
                self.just_fired = obj

    def update(self, time_passed):
        """Update Zapper"""
        self.even_frame = not self.even_frame
        if self.invincible:
            self.invincible_time -= time_passed
            if self.invincible_time < 0:
                self.invincible = False
        for item in self.current_items:
            self.current_items[item].total_time += time_passed
        self.just_fired = False
        if self.dead and self.health > 0:
            self.im_back = True
            self.dead = False
            self.frame = 1
        if self.regen:
            self.regen_time += time_passed
            t = 1
            if self.shield == 0:
                t = 2
            if self.regen_time >= t:
                self.regen_time = 0
                self.shield += .1
                if self.shield > self.max_shield:
                    self.shield = self.max_shield
        pressed = pygame.key.get_pressed()
        if (pressed[pygame.K_SPACE] or pressed[pygame.K_w] or pressed[pygame.K_UP] or joystick.CurrentState.X) and self.completeness == 1 and self.canFire and self.beam and not self.dead:
            obj = self.fire()
            if not self.whimp:
                self.just_fired = obj
        if pressed[pygame.K_q] and self.rotate:
            self.rotation -= self.rotation_speed * time_passed
        if joystick.CurrentState.LT_val >= .05 and self.rotate:
            self.rotation -= self.rotation_speed * time_passed * joystick.CurrentState.LT_val

        if pressed[pygame.K_e] and self.rotate:
            self.rotation += self.rotation_speed * time_passed
        if joystick.CurrentState.RT_val >= .05 and self.rotate:
            self.rotation += self.rotation_speed * time_passed * joystick.CurrentState.RT_val

        if self.rotation < -self.max_rotation:
            self.rotation = -self.max_rotation
        if self.rotation > self.max_rotation:
            self.rotation = self.max_rotation
        if self.dead:
            if self.frame_rate <= self.frame_time:
                self.frame += 1
                self.frame_time = 0
            if self.frame > self.death_frames:
                self.kill = True
                self.frame = 25
            self.frame_time += time_passed
        self.time_passed = time_passed
        if self.completeness < 1:
            self.completeness += time_passed * self.fire_per_sec
        if self.completeness > 1:
            self.completeness = 1
        if not self.beam:
            self.image = pygame.transform.scale(self.images[\
                f"{self.name}{int(6 * (self.completeness / 1))}"], self.size)
        acc = True
        if (pressed[pygame.K_LEFT] or pressed[pygame.K_a] or joystick.CurrentState.joystick_left) and not self.dead:
            self.target_x_velocity = -self.max_velocity
        elif (pressed[pygame.K_RIGHT] or pressed[pygame.K_d] or joystick.CurrentState.joystick_right) and not self.dead:
            self.target_x_velocity = self.max_velocity
        else:
            acc = False
            self.target_x_velocity = 0
        if acc:
            self.velocity.x -= (self.velocity.x - self.target_x_velocity) * self.speed * self.friction * (1 if self.hover else self.mission.friction * self.mission.traction) * self.acceleration * self.general_acc * self.time_passed
        if not acc:
            self.velocity.x -= (self.velocity.x - self.target_x_velocity) * self.friction * (1 if self.hover else self.mission.friction) * self.general_acc * self.time_passed
        if self.velocity.x > self.max_velocity:
            self.velocity.x = self.max_velocity
        if self.velocity.x < -self.max_velocity:
            self.velocity.x = -self.max_velocity
        if abs(self.velocity.x) < .01 and not acc:
            self.velocity.x = 0
        if self.pos[0] <= 0 and self.velocity.x < 0:
            self.velocity.x = abs(self.velocity.x) * .2
        if self.rect.right >= 800 and self.velocity.x > 0:
            self.velocity.x = -abs(self.velocity.x) * .2
#        if self.pos[0] < 0:
#            self.pos[0] = 0
#            self.velocity[0] = 0
#        if self.pos[0] > 736:
#            self.pos[0] = 736
#            self.velocity[0] = 0
        if self.mission.temperature + self.add_temp > self.max_temp and not self.dead:
            remove = ((self.mission.temperature + self.add_temp - self.max_temp) / 1000) * self.time_passed
            if self.shield > 0:
                self.shield -= remove
            else:
                self.health -= remove
            if self.shield < 0:
                self.shield = 0
        self.pos[0] += self.velocity[0]
        self.pos[1] += self.velocity[1]
        self.rect = self.get_rect()
        if not self.dead:
            self.rect.bottom -= ((self.rect.bottom - self.target_alt) * self.alt_change_speed * self.time_passed)
        self.pos[1] = self.rect.top
        self.rect = self.get_rect()

    def goToGround(self):
        self.target_alt = self.min_alt

    def goBackUp(self):
        self.target_alt = self.standard_alt

class VenusCrawler(Zapper):
    def __init__(self, pos, images, mission, dry = False):
        super().__init__(pos, images, mission, dry)
        self.title = "Venus Crawler"
        self.name = "venus_crawler"
        self.death_frames = 15
        self.mass = 3
        self.speed = 20
        self.health = 2
        self.friction = 1.5
        self.max_health = 2
        self.max_shield = 2
        self.max_temp = 950 # Works up to 950 deg. F
        self.fire_from = (22, 32)
        self.fire_per_sec = 5
        self.send_to_ground()

class Curiosity(Zapper):
    def __init__(self, pos, images, mission, dry = False):
        super().__init__(pos, images, mission, dry)
        self.title = "Curiosity"
        self.name = "curiosity"
        self.death_frames = 15
        self.size = (62, 38)
        self.boom_size = (256, 256)
        self.fire_from = (40, 6)
        self.fire_per_sec = 50
        self.health = .5
        self.speed *= 1.3
        self.max_health = .5
        self.shield = .5
        self.max_shield = .5
        self.rect = self.get_rect()
        self.always_beam = True
        self.beam = True
        self.rotate = True
        self.whimp = True
        self.send_to_ground()
        self.mass = 2

class JupiterHover(Zapper):
    def __init__(self, pos, images, mission, dry = False):
        super().__init__(pos, images, mission, dry)
        self.title = "Jupiter Hovercraft"
        self.name = "jupiter_hover"
        self.fire_per_sec = 6.5
        self.death_frames = 21
        self.size = (32, 32)
        self.boom_size = (256, 256)
        self.fire_from = (24, 5)
        self.health = .75
        self.max_health = .75
        self.shield = 0
        self.max_shield = 2
        self.rect = self.get_rect()
        self.hover = True
        self.rotate = True
        self.mass = .75
        self.max_temp = 500
        self.hover_alt = 430
        self.frame_rate = 1/35
        self.extra_dip = 10
        self.speed *= .8
        self.friction = .5
        self.send_to_ground()
        self.weapon_power = .75
        self.death_sound = Sound(fix_path("audio/jupiter_hover_explode.wav"), True)
