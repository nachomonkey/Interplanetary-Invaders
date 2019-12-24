import sys
import shelve
import random
import pygame
import time
import copy
import os
import math
from pygame.math import Vector2
from math import radians, cos, sin

from ii_game.scripts import lightning
from ii_game.scripts import constants
from ii_game.scripts import items
from ii_game.scripts import screenshot
from ii_game.scripts import joystick
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts.transition import transition
from ii_game.scripts.pause_menu import pause_menu
from ii_game.scripts.gameobject import GameObject
from ii_game.scripts.utils import fix_path, colorize
from ii_game.scripts.sound import Sound
from ii_game.scripts.lasers import *
from ii_game.scripts import saves

pygame.mixer.pre_init(44100, 16)
pygame.init()

CLOCK = pygame.time.Clock()

METER = .006 # 1 / METER pixels = 1 meter

G = 9.81 # Acceleration of Earth's gravity in m/s^2

SIZE = (800, 600)

GRAVITY = G * 1

shared = {"money_ser_num" : 0, "options" : saves.load_options(), "cat" : []}

NUM_KEYS = [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0]
NUMPAD_KEYS = [pygame.K_KP1, pygame.K_KP2, pygame.K_KP3, pygame.K_KP4,
pygame.K_KP5, pygame.K_KP6, pygame.K_KP7, pygame.K_KP8, pygame.K_KP9,
pygame.K_KP0]

pygame.mixer.set_num_channels(50)

def draw_bar(prog, center, surf, max_health, max_shield, shield=0, color=(0, 255, 0), back=(10, 10, 10), width=150, height=20, r=True):
    if prog <= 0 and shield <= 0:
        return
    if prog < 0:
        prog = 0
    rect = pygame.Rect((0, 0), (width, height))
    rect.center = center
    rect2 = rect.copy()
    rect3 = rect.copy()
    if prog > max_health:
        prog = max_health
    if r:
        if prog / max_health < .97:
            rect.w *= int(prog * 10) / 10 / max_health
        if shield / max_shield < .97:
            rect3.w *= int(shield * 10) / 10 / max_shield
    else:
        rect.w *= prog / max_health
        rect3.w *= shield / max_shield
    pygame.draw.rect(surf, back, rect2)
    pygame.draw.rect(surf, color, rect)
    if shield:
        pygame.draw.rect(surf, (0, 100, 150), rect3)
    for x in range(0, width, 11):
        pygame.draw.line(surf, (0, 0, 0), (rect.left + x, rect.top), (rect.left + x, rect.bottom - 1), 1)


def exit_game():
    """Exit Game"""
    pygame.quit()
    sys.exit()

MAIN_TEXT_COLOR = (200, 200, 200)

class Game:
    """This class runs the game, and contains the game's logic"""

    def __init__(self, display, Display, images, mission, profile, profile_selected):
        """Initialize Game Class"""
        self.Display = Display
        self.display = display
        self.images = images
        self.mission = mission()
        self.mission_type = mission
        self.profile, self.profile_selected = profile, profile_selected
        self.toMenu = False
        self.aliens = []
        self.alien_time = 0
        self.time_passed = 0
        self.points = []
        self.score = 0
        self.next_wave = self.mission.patterns.pop(0)
        self.next_alien = random.uniform(*self.next_wave.rate)
        self.aliens_killed = 0
        self.GOs = []
        self.bossed = False
        self.ran_out_of_aliens = False
        self.green_lightning_sound = Sound(fix_path("audio/lightning2.wav"))
        self.lightning_sound = Sound(fix_path("audio/lightning.wav"))
        self.gls = self.green_lightning_sound.play(-1)
        self.gls.set_volume(0)
        self.ls = self.lightning_sound.play(-1)
        self.ls.set_volume(0)
        self.flaks = []
        self.charging = 0
        self.crg = False
        self.options = saves.load_options()
        self.done = False
        self.endgame = None
        self.end_timer = 0
        self.next_airplane = random.uniform(1, 4)
        self.airplane_time = 0
        self.next_meteor_shower = random.uniform(8, 20)
        self.next_solar_flare = random.uniform(15, 40)
        self.sft = 0
        self.sf = 0
        self.mst = 0
        self.volcanoes = []
        screenshot.options = saves.load_options()
        if self.mission.planet.name == "Venus":
            for x in range(2):
                self.volcanoes.append(Volcano(random.randint(0, 800), self.images))
        self.point = None
        for x in self.profile["map"][self.profile["planet"].name]:
            if x.mission == self.mission_type:
                self.point = x
        self.loser = False
        if self.point:
            if self.point.lost > 7:        # Are you a loser?
                self.loser = True          # You ARE a loser?!?
                self.GOs.append(GameObject((250, 0), images, self.mission, "block", value=items.FireItem2x))
                self.mission.item_mul *= 1.5
                self.mission.items *= 2
        self.notimer = True
        self.accuracy = []
        self.lasers_to_track = []
        self.combo = 0
        self.combos = []
        self.i10l = store_data.ItemStorage10 in self.profile["inventory"][2]
        self.item_progress = 0

    def main(self):
        """Running this method runs the game"""
        self.briefing(self.mission)
        c = shared["cat"]
        ca = None
        if c and self.mission.__class__ == shared["mission"].__class__:
            ca = c
        inv = Inventory(self.Display, self.images, self.profile, ca, None)
        self.profile, cat, player, sel = inv.main()
        shared["cat"] = sel
        shared["mission"] = self.mission
        itms = cat[-1]
        self.player = player([400, 431], self.images, self.mission)
        for r, i in itms:
            if i:
                self.player.items.append(i.link())
        if self.loser:
            self.free_item()
        self.brought_items = bool(self.player.items)
        self.AddKilledAlien(True)
        self.keepGoing()
        self.combos.append(self.combo)
        self.gls.stop()
        self.ls.stop()
        for g in self.GOs:
            if g.type == "aircraft":
                self.GOs[self.GOs.index(g)].jet_sound.stop()
        if self.endgame == "won":
            for i in self.player.items:
                store_item = store_data.ITEMS[items.items.index(i.__class__)]
                if store_item in self.profile["inventory"][0]:
                    self.profile["inventory"][0][store_item] += 1
                else:
                    self.profile["inventory"][0][store_item] = 1
        screenshot.update(self.Display)
        return self.score, self.endgame, self.accuracy, max(self.combos), self.player.im_back

    def keepGoing(self):
        try:
            while not self.done:
                self.events()
                self.draw()
                self.update()
        except KeyboardInterrupt:
            if self.brought_items:
                print(colorize("Hey! Complete the level!", "fail"))
                self.keepGoing()
            else:
                exit_game()

    def deploy_item(self):
        self.notimer = True
        joystick.Reset()
        done = False
        sel = 0
        num_boxes = 5
        if self.i10l:
            num_boxes = 10
        bigBox = pygame.Rect(0, 0, 550, 300)
        bigBox.center = self.Display.get_rect().center
        boxHolder = pygame.Rect(0, 0, 0, 0)
        BOX_SIZE = 50
        boxHolder.w = BOX_SIZE * num_boxes
        boxHolder.h = BOX_SIZE
        boxHolder.center = self.Display.get_rect().center
        boxes = []
        for x in range(num_boxes):
            boxes.append(pygame.Rect(boxHolder.x + (x * BOX_SIZE), boxHolder.y, BOX_SIZE, BOX_SIZE))
        display = self.Display.copy()
        for e, item in enumerate(self.player.items):
            if item:
                sel = e
                break
        while not done:
            for event in pygame.event.get():
                joystick.Update(event)
                if not hasattr(event, "key"):
                    event.key = None
                if event.type == pygame.KEYDOWN or joystick.WasEvent():
                    if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                        done = True
                    if event.key == pygame.K_LEFT or joystick.JustWentLeft():
                        sel -= 1
                    if event.key == pygame.K_RIGHT or joystick.JustWentRight():
                        sel += 1
                    if sel < 0:
                        sel = 0
                    if sel >= num_boxes:
                        sel = num_boxes - 1
                    if event.key == pygame.K_RETURN or joystick.JustPressedA():
                        if (len(self.player.items) > sel):
                            self.activate_item(sel)
                        else:
                            Sound(fix_path("audio/donk.wav")).play()
                        if not self.player.items:
                            done = True
            self.Display.blit(display, (0, 0))
            pygame.draw.rect(self.Display, (45, 45, 45), bigBox)
            pygame.draw.rect(self.Display, (255, 255, 0), bigBox, 1)
            pygame.draw.rect(self.Display, (40, 40, 40), boxHolder)
            retro_text((bigBox.move(0, 35).midtop), self.Display, 15, "Deploy Items", anchor="center", bold=True)
            for e, box in enumerate(boxes):
                color = (0, 0, 0)
                if sel == e:
                    color = (255, 255, 0)
                if (len(self.player.items) > e):
                    item = self.player.items[e]
                    if item:
                        image = pygame.transform.scale(self.images[item.image], box.size)
                        image_rect = image.get_rect()
                        image_rect.center = box.center
                        self.Display.blit(image, image_rect)
                    if sel == e:
                        retro_text((boxHolder.move(0, 10).midbottom), self.Display, 14, item.name, anchor="midtop")
                pygame.draw.rect(self.Display, color, box, 1)
            pygame.display.update()
        joystick.Reset()

    def free_item(self):
        display = self.Display.copy()
        rect = pygame.Rect(0, 0, 600, 400)
        rect.center = self.display.get_rect().center
        done = False
        while not done:
            for event in pygame.event.get():
                joystick.Update(event)
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_q, pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                        done = True
                if joystick.WasEvent():
                    if joystick.GoEvent() or joystick.BackEvent():
                        done = True
            self.Display.blit(display, (0, 0))
            pygame.draw.rect(self.Display, (40, 40, 40), rect)
            pygame.draw.rect(self.Display, (255, 255, 0), rect, 1)
            retro_text((rect.move(0, 28).midtop), self.Display, 14, "You seem to be having a hard time...", anchor="center", color=(0, 0, 0), bold=True)
            retro_text((rect.move(0, 26).midtop), self.Display, 14, "You seem to be having a hard time...", anchor="center", bold=True)
            retro_text((rect.move(0, 67).midtop), self.Display, 15, "Here is a FREE 2x fire rate item!", anchor="center", color=(0, 0, 0))
            retro_text((rect.move(0, 65).midtop), self.Display, 15, "Here is a FREE 2x fire rate item!", anchor="center")
            img = pygame.transform.scale(self.images["2xfireitem"], (100, 100))
            r = img.get_rect()
            r.center = rect.center
            self.Display.blit(img, r)
            pygame.draw.rect(self.Display, (0, 0, 0), r, 1)
            pygame.display.update()
        joystick.Reset()

    def victory(self):
        planet = self.profile["planet"]
        for point in self.profile["map"][planet.name]:
            if point.mission == self.mission_type:
                point.alien_flag = False
                point.type = point.will_be
                point.name = point.next_name
                point.completed = True
        self.profile["money"] += round(self.score)
        saves.save_data(self.profile_selected, self.profile)
        self.done = True

    def briefing(self, mission):
        done = False
        frame = 1
        next_frame = 1 / 10
        frame_time = 0
        time_passed = 0
        star_frame_time = 0
        next_star_frame = 1 / 10
        star_frame = 1
        deg = 0
        temp_diff = 0
        mx_temp_diff = 15   # +/- mx_temp_diff
        mx_temp_change = .1
        temp_dir = 0
        while not done:
            if not random.randint(0, 10):
                temp_dir = random.randint(0, 1)
            if temp_dir == 0:
                temp_dir = -1
            temp_diff += random.uniform(0, temp_dir * mx_temp_change)
            if temp_diff > mx_temp_diff:
                temp_diff = mx_temp_diff
                temp_dir *= -1
            if temp_diff < -mx_temp_diff:
                temp_diff = -mx_temp_diff
                temp_dir *= -1
            for event in pygame.event.get():
                joystick.Update(event)
                if not hasattr(event, "key"):
                    event.key = None
                if event.type == pygame.QUIT:
                    exit_game()
                if event.type == pygame.KEYDOWN or joystick.WasEvent():
                    if event.key == pygame.K_RETURN or joystick.GoEvent():
                        done = True
                    if event.key == pygame.K_F2 or joystick.JustPressedLB():
                        screenshot.capture(self.profile_selected, self.display)
            self.display.blit(self.images["briefing"], (0, 0))
            self.display.blit(self.images[f"flying_stars{star_frame}"], (390, 45))
            size = round(100 - (math.sin(deg) * 10))
            r1 = pygame.Rect(515, 85, 100, 100)
            r2 = pygame.Rect(0, 0, size, size)
            r2.center = r1.center
            self.display.blit(pygame.transform.scale(self.images[f"spinning{mission.planet.name}{frame}"], (size, size)), r2)
            pos = [155, 350]
            size = 14
            retro_text((60, 90), self.display, 18, "Planetary Specs:", res = 14, font = "Sans")
            retro_text((60, 110), self.display, 16, f"Gravity: {mission.planet.gravity} G", res = 14)
            t, tr = retro_text((60, 125), self.display, 16, f"Surf. Temperature: {mission.temperature + round(temp_diff, 2)} F", res = 14, render = False)
            self.display.blit(pygame.transform.scale(t, (round(t.get_width() * .65), 16)), tr.topleft)
            for y, text in enumerate(mission.briefing.split("\n")):
                retro_text((pos[0], pos[1] + y * size), self.display, size, text, res = 13, font = "Sans")
            if frame_time >= next_frame:
                frame += 1
                frame_time = 0
            if frame > 25:
                frame = 1
            if star_frame_time >= next_star_frame:
                star_frame += 1
                star_frame_time = 0
            if star_frame > 100:
                star_frame = 1
            deg += time_passed / 500
            time_passed = CLOCK.tick(25)
            frame_time += time_passed
            star_frame_time += time_passed
            self.Display.blit(pygame.transform.scale(self.display, SIZE), (0, 0))
            pygame.display.update()
        joystick.Reset()

    def calc_height(self):
        pos = [0, self.player.get_rect().centery]
        amount = (-4000 * (time.time() - self.charging))
        rotation = self.player.rotation
        velocity = pygame.Vector2([(cos(radians(rotation + 90)) * amount), (sin(radians(rotation + 90)) * amount)])
        lp = pos
        while True:
            velocity[1] += (self.mission.planet.gravity * G) * self.time_passed / METER
            lp = copy.copy(pos)
            x = self.player.get_rect().left + self.player.fire_from[0] + pos[0]
            if x < 0:
                velocity[0] = abs(velocity[0])
            if x > 800:
                velocity[0] = -abs(velocity[0])
            pos[0] += velocity[0] * self.time_passed
            pos[1] += velocity[1] * self.time_passed
            if lp[1] < pos[1]:
                break
        return pos

    def add_points(self, amount, pos, mseg = False):
        if not mseg:
            if self.player.current_items and amount > 0:
                if "2x Money Bonus" in self.player.current_items:
                    amount *= 2
            if self.player.title == "Curiosity" and amount > 0:
               amount *= 2
            amount = round(amount)
            self.score += amount
        rect = pygame.Rect((0, 0), (25, 25))
        rect.bottomleft = pos
        hitTop = False
        while True:
            img = retro_text(rect.topright, self.display, 20, amount, anchor = "bottomleft", render = False, font = "impact")
            yes = True
            if img[1].top < 0:
                hitTop = True
                yes = False
            for p in self.points:
                if p[0][1].colliderect(img[1]):
                    yes = False
            if yes:
                break
            else:
                if hitTop:
                    rect.y += 20
                else:
                    rect.y -= 20
        self.points.append([img, time.time()])

    def events(self):
        """Collect and handle user events"""
        for event in pygame.event.get():
            joystick.Update(event)
            if not hasattr(event, "key"):
                event.key = None
            if event.type == pygame.QUIT and not self.brought_items:
                exit_game()
            if event.type == pygame.KEYUP or joystick.WasEvent():
                if (event.key == pygame.K_LSHIFT or joystick.EndEvent("A")) and "Flak Bursts" in self.player.current_items and self.player.completeness == 1:
                    self.flaks.append(Flak(self.images, self.player.get_rect().center, self.mission, time.time() - self.charging, self.player.rotation))
                    if "2x Fire Rate" in self.player.current_items:
                        self.flaks.append(Flak(self.images, self.player.get_rect().center, self.mission, (time.time() - self.charging), self.player.rotation - 10))
                        self.flaks.append(Flak(self.images, self.player.get_rect().center, self.mission, (time.time() - self.charging), self.player.rotation + 10))
                    self.player.completeness = 0
                    self.crg = False
                if (event.key == pygame.K_DOWN or joystick.JustStoppedHalfDown()) and self.player.hover:
                    self.player.goBackUp()
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                if event.key == pygame.K_F2 or joystick.JustPressedLB():
                    screenshot.capture(self.profile_selected, self.display, True)
                if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                    self.toMenu = pause_menu(self.Display, self.images, self.profile, self.profile_selected, self.brought_items)
                    self.done = self.toMenu
                    self.options = saves.load_options()
                    screenshot.options = self.options
                    self.notimer = True
                if (event.key == pygame.K_y or joystick.JustPressedY()) and not self.player.dead:
                    self.deploy_item()
                if (event.key == pygame.K_LSHIFT or joystick.StartEvent("A")) and "Flak Bursts" in self.player.current_items:
                    self.charging = time.time()
                    self.crg = True
                for e, item in enumerate(self.player.items):
                    if event.key == NUM_KEYS[e] or event.key == NUMPAD_KEYS[e]:
                        self.activate_item(e)
                if (event.key == pygame.K_DOWN or joystick.JustWentHalfDown()) and self.player.hover:
                    self.player.goToGround()
            self.player.events(event)

    def activate_item(self, e):
        item = self.player.items.pop(e)
        if self.player.current_items:
            if item.name in self.player.current_items:
                self.player.current_items[item.name].length += item.length
                return
        else:
            self.player.current_items[item.name] = item
        item.activate()
        self.player.current_items[item.name] = item
        if item.name == "Green Laser":
            self.player.fireObject = GreenLaser
            if "Lightning" in self.player.current_items:
                lightning.GREEN_ON = True
        if item.name == "2x Fire Rate":
            self.player.fire_per_sec *= 2
            if "Lightning" in self.player.current_items:
                lightning.MAX_THINGS *= 3
        if item.name == "2x Speed":
            self.player.max_velocity *= 2
        if item.name == "Lightning":
            self.player.canFire = False
            if "Green Laser" in self.player.current_items:
                lightning.GREEN_ON = True
            if "2x Fire Rate" in self.player.current_items:
                lightning.MAX_THINGS *= 3
        if item.name == "Auto Gun":
            self.player.beam = True
        if item.name == "Shield Regenerator":
            self.player.regen = True
        if item.name == "Magnet":
            for go in self.GOs:
                go.tracking_speed = constants.ATTRACTION_WITH_MAGNET.get(go.type, 0) * self.mission.magnet_power

    def draw(self):
        """Render the game"""
        self.display.blit(self.images["background"], (0, 0))
        self.display.blit(self.images[self.mission.backdrop], (0, 0))
        for v in self.volcanoes:
            v.draw(self.display)
        if "Flak Bursts" in self.player.current_items and self.crg:
            x, y = self.calc_height()
            x, y = round(x), round(y)
            cx, cy = self.player.get_rect().center
            pygame.draw.circle(self.display, (30, 30, 30), (cx + x, y), 20)
            pygame.draw.circle(self.display, (0, 0, 0), (cx + 2 + x, y + 2), 20)
            pygame.draw.circle(self.display, (125, 125, 125), (cx + x, y), 20, 2)
            pygame.draw.line(self.display, (255, 0, 0), (cx - 10 + x, y), (cx + x + 10, y), 2)
            pygame.draw.line(self.display, (255, 0, 0), (cx + x, y - 10), (cx + x, y - 10), 2)
        for go in self.GOs:
            go.draw(self.display)
        for laser in self.player.lasers:
            laser.draw(self.display)
        for alien in self.aliens:
            alien.draw(self.display)
        lightning_on = len(self.aliens) > 0
        if "Lightning" in self.player.current_items and (pygame.key.get_pressed()[pygame.K_SPACE] or joystick.CurrentState.X):
            lightning.run(self.player.get_rect().center, self.aliens, self.GOs, self.player, self.display, self.time_passed)
            if lightning_on:
                if lightning.GREEN_ON:
                    self.gls.set_volume(1)
                else:
                    self.ls.set_volume(1)
        else:
            lightning_on = False
        if not lightning_on:
            self.ls.set_volume(0)
            self.gls.set_volume(0)
        self.player.draw(self.display)
        retro_text((602, 2), self.display, 18, "Health:", anchor = "midtop", color = (0, 0, 0))
        retro_text((600, 0), self.display, 18, "Health:", anchor = "midtop", color=MAIN_TEXT_COLOR)
        retro_text((602, 77), self.display, 18, f"Loot: {self.score}", anchor = "midtop", color = (0, 0, 0))
        retro_text((600, 75), self.display, 18, f"Loot: {self.score}", anchor = "midtop", color=MAIN_TEXT_COLOR)
        retro_text((402, 2), self.display, 16, f"Aliens Killed: {self.aliens_killed} / {self.mission.aliens}", anchor = "midtop", font = "impact", color = (0, 0, 0))
        retro_text((400, 0), self.display, 16, f"Aliens Killed: {self.aliens_killed} / {self.mission.aliens}", anchor = "midtop", font = "impact", color=MAIN_TEXT_COLOR)
        if self.combo:
            retro_text((402, 28), self.display, 16, f"Combo: {self.combo}", anchor="midtop", font="impact", color=(0, 0, 0))
            retro_text((400, 30), self.display, 16, f"Combo: {self.combo}", anchor="midtop", font="impact", color=MAIN_TEXT_COLOR)
        draw_bar(self.player.health, (600, 40), self.display, self.player.max_health, self.player.max_shield, self.player.shield)
        color = (150, 35, 0)
        if self.mission.items <= self.mission.items_dropped:
            color = (210, 200, 0)
        draw_bar(self.item_progress, (400, 20), self.display, 1, 1, color=color, back=(30, 30, 30), width=300, height=6, r=False)
        draw_bar(self.mission.getProgTillNextItem(self.aliens_killed), (400, 27), self.display, 1, 1, color=(0, 150, 0), back=(30, 30, 30), width=300, height=6, r=False)
        image = "itemHolder"
        minus = 0
        if self.i10l:
            image = "itemHolder10"
            minus = 45
        self.display.blit(self.images[image], (550 - minus, 100))
        for e, item in enumerate(self.player.items):
            pos = (552 - minus + (e * 19), 102)
            self.display.blit(self.images[item.image], pos)
            pos2 = list(pos)
            pos2[1] += 18
            retro_text(pos2, self.display, 14, e + 1, anchor = "topleft")
        Items = self.player.current_items
        for e, item in enumerate(self.player.current_items):
            self.display.blit(self.images[Items[item].image], (525, 140 + e * 20))
            retro_text((600, 140 + e * 20), self.display, 18, round(Items[item].length - Items[item].total_time, 2), anchor = "midtop")
        for flak in self.flaks:
            flak.draw(self.display)
        for p in self.points:
            self.display.blit(*p[0])
            if time.time() - p[1] >= 1.5:
                del self.points[self.points.index(p)]
        if self.sf:
            sf_surf = pygame.Surface((800, 600))
            sf_surf.fill((254, 246, 229))
            sf_surf.set_alpha(255 * self.sf)
            self.display.blit(sf_surf, (0, 0))
        self.Display.blit(pygame.transform.scale(self.display, SIZE), (0, 0))

    def kill_laser(self, laser):
        if laser in self.lasers_to_track:
            if laser.hits:
                for x in range(laser.hits):
                    self.accuracy.append(True)
                    self.combo += 1
            else:
                self.accuracy.append(False)
                self.combos.append(self.combo)
                self.combo = 0
            self.lasers_to_track.remove(laser)
        del self.player.lasers[self.player.lasers.index(laser)]

    def AddKilledAlien(self, start=False):
        if not start:
            self.aliens_killed += 1
        if self.aliens_killed in self.mission.programmed_items and not start:
            Val = self.mission.programmed_items.pop(self.aliens_killed)
            if not type(Val) == list:
                Val = [Val]
            for i in Val:
                self.GOs.append(GameObject((400, 0), self.images, self.mission, "block", value=i))
            self.mission.last_aliens_killed = self.aliens_killed
        if start:
            if 0 in self.mission.programmed_items:
                items = []
                obj = self.mission.programmed_items.pop(0)
                if type(obj) in (list, tuple, set):
                    items = obj
                else:
                    items = [obj]
                for item in items:
                    self.player.items.append(item())

    def update(self):
        """Game Logic / Wait for next frame"""
        add_temp = False
        if self.mission.solar_flares:
            self.sft += self.time_passed
            if self.sft >= self.next_solar_flare:
                self.next_solar_flare = random.uniform(15, 40)
                self.sft = 0
                for a in self.aliens:
                    if not a.isBoss:
                        a.health -= 1 * random.uniform(.7, 2.5)
                        if a.health < 0:
                            a.health = 0
                            a.dead = 1
                            a.explode_sound.play()
                            self.AddKilledAlien()
                for go in self.GOs:
                    if go.type in ("mine", "moneyBag", "rock"):
                        go.dead = True
                for f in self.flaks:
                    f.dead = True
                if self.mission.temperature + 500 > self.player.max_temp:
                    remove = ((self.mission.temperature + 500 - self.player.max_temp) / 1000)
                    if self.player.shield > 0:
                        self.player.shield -= remove / 2
                    else:
                        self.player.health -= remove
                    if self.player.shield < 0:
                        self.player.shield = 0
                self.sf = 1
        if self.sf:
            self.sf -= self.time_passed
            if self.sf < 0:
                self.sf = 0
        for v in self.volcanoes:
            v.update(self.time_passed)
            if self.player.get_rect().colliderect(v.rect) and v.erupting:
                self.player.add_temp = 600
                add_temp = True
        if not add_temp:
            self.player.add_temp = 0
        if self.mission.planet.name == "Mars":
            self.mst += self.time_passed
            if self.mst >= self.next_meteor_shower:
                self.mst = 0
                self.next_meteor_shower = random.uniform(8, 20)
                num = random.randint(3, 15)
                direction = random.randint(0, 1)
                if direction == 0:
                    direction = -1
                velX = random.randint(250, 400)
                velY = random.randint(50, 75)
                posX = random.randint(0, 800)
                for x in range(num):
                    self.GOs.append(GameObject((posX - (20 * x), 30 - (15 * x)), self.images, self.mission, type="rock", velocity = [velX * direction, velY], nobounce=True))
        if not len(self.aliens) and self.bossed and self.ran_out_of_aliens and not self.end_timer:
            self.end_timer = time.time()
        if self.end_timer:
            if time.time() - self.end_timer >= 2:
                self.endgame = "won"
        self.airplane_time += self.time_passed
        if self.next_airplane <= self.airplane_time and self.mission.airport:
            self.GOs.append(GameObject((0, 0), self.images, self.mission, "aircraft"))
            self.airplane_time = 0
            self.next_airplane = random.uniform(1, 4)
        if self.player.just_fired:
            self.lasers_to_track.append(self.player.just_fired)
        self.player.update(self.time_passed)
        for f in self.flaks:
            if f.kill:
                self.flaks.remove(f)
            d1 = f.dead
            for a in self.aliens:
                if f.get_rect2().colliderect(a.get_rect()) and not f.dead and not f.isBomb:
                    f.dead = True
                    f.sound.play()
            for g in self.GOs:
                if g.get_rect().colliderect(f.get_rect2()) and not f.dead and not f.isBomb:
                    f.dead = True
                    f.sound.play()
            if f.isBomb:
                for l in self.player.lasers:
                    if l.get_rect().colliderect(f.get_rect()) and not f.dead and (f.hitBy or l.green) and f.hitBy != l and not l.dead:
                        f.dead = True
                        f.sound.play()
                    if not f.hitBy and not l.green and l.get_rect().colliderect(f.get_rect()):
                        self.player.lasers.remove(l)
                    f.hitBy = l
            f.update(self.time_passed)
            if not d1 and f.dead:
                if f.isBomb:
                    cx1, cy1 = self.player.get_rect().center
                    cx2, cy2 = f.get_rect().center
                    dist = math.hypot(cx1 - cx2, cy1 - cy2)
                    damage = 2 * ((128 - dist) / 128)
                    if damage > 0:
                        if not self.player.shield:
                            self.player.health -= damage
                            if self.player.health < 0:
                                self.player.health = 0
                        else:
                            self.player.shield -= damage
                            if self.player.shield < 0:
                                self.player.shield = 0
                        self.add_points(round(-150 * damage), f.get_rect().move(0, -100).center)
                hitSome = False
                for a in self.aliens + self.GOs:
                    cx1, cy1 = a.get_rect().center
                    cx2, cy2 = f.get_rect().center
                    dist = math.hypot(cx1 - cx2, cy1 - cy2)
                    stuff = ("rock", "moneyBag", "airplane")
                    if a in self.GOs:
                        if a.type in (["moneyBag"] if f.isBomb else stuff) and dist < 256 and not a.dead:
                            if a.type == "moneyBag" and not f.isBomb:
                                self.profile["money_killed"] += 1
                            a.dead = True
                            a.frame = 1
                        continue
                    if f.isBomb:
                        continue
                    damage = 10 * ((256 - dist) / 256)
                    if a.hitBy != f and damage > 0:
                        a.health -= round(damage, 2)
                    if a.health <= 0:
                        f.hits += 1
                        a.hitBy = f
                        self.combo += 1
                        hitSome = True
                if not hitSome:
                    self.combos.append(self.combo)
                    self.combo = 0
        if self.player.health <= 0 and not self.player.dead:
            self.player.dead = True
            if self.player.death_sound:
                self.player.death_sound.play()
        if self.player.kill:
            self.player.health = 0
            self.endgame = "lost"
        for laser in self.player.lasers:
            laser.update(self.time_passed)
            if laser.kill:
                self.kill_laser(laser)
            for go in self.GOs:
                if laser.get_rect().colliderect(go.get_rect()) and not go.dead and not laser.dead:
                    if go.type == "rock":
                        go.dead = True
                        go.frame = 1
                    if go.type == "mine" and not go.hitBy == laser:
                        go.health -= laser.damage / 2
                        go.lifetime += 1
                        go.hitBy = laser
        for go in self.GOs:
            if not go.player:
                go.player = self.player
                go.update_attraction()
            go.update(self.time_passed)
            for l in self.player.lasers:
                if l.get_rect().colliderect(go.get_rect()) and go.type == "aircraft" and not go.dead and not laser.dead:
                    self.player.lasers.remove(l)
                    go.dead = True
                    go.gotShot = True
                    go.frame_rate = 1 / 25
                    Sound(fix_path("audio/flak.wav")).play()
            if go.kill:
                if go.type == "aircraft" and go.gotShot:
                    self.endgame = "lost"
                self.GOs.remove(go)
                continue
            if go.type == "rock":
                for go2 in self.GOs:
                    if go2.type == "moneyBag" and not go2.dead:
                        if not go.dead and not go in go2.hitBy and go.get_rect().colliderect(go2.get_rect()):
                            go2.hitBy.append(go)
                            go2.health -= .5
                            go2.frame = 1
            if go.health <= 0 and not go.type == "mine":
                go.dead = True
            if go.health < go.start_health and not go.dead and not go.life_bar:
                go.life_bar = True
            kaboom = False
            if go.lifetime > go.max_lifetime and go.type == "mine" and not go.dead:
                kaboom = True
            if go.get_rect().colliderect(self.player.get_rect()):
                if go.type == "moneyBag" and not go.dead:
                    if go.amount != None:
                        self.add_points(go.amount, go.get_rect().center)
                    else:
                        self.add_points(random.choice([100] * 5 + [250, 350, 450, 500, 650, 1000]), go.get_rect().center)
                    del self.GOs[self.GOs.index(go)]
                if go.type == "heart":
                    self.player.health = self.player.max_health
                    self.add_points(150, go.get_rect().center)
                    Sound(fix_path("audio/heart.wav")).play()
                    del self.GOs[self.GOs.index(go)]
                if go.type == "shield":
                    Sound(fix_path("audio/shield.wav")).play()
                    self.add_points(150, go.get_rect().center)
                    self.player.shield += 1
                    if self.player.shield > self.player.max_shield:
                        self.player.shield = self.player.max_shield
                    self.GOs.remove(go)
                if go.type in ("rock", "laser") and not go.dead and not go in self.player.hitBy:
                    self.player.hitBy.append(go)
                    if self.player.shield > 0:
                        self.player.shield -= .5
                        if self.player.shield < 0:
                            self.player.shield = 0
                            self.add_points(-75, go.get_rect().center)
                    else:
                        self.player.health -= .5
                        self.add_points(-100, go.get_rect().center)
                if go.type == "block":
                    Sound(fix_path("audio/item.wav")).play()
                    self.GOs.remove(go)
                    if go.value == None:
                        item = self.mission.getItem()
                    else:
                        item = go.value()
                    self.player.items.append(item)
                    self.add_points(250, (go.get_rect().centerx, go.get_rect().y + 100))
                    self.add_points(item.name, go.get_rect().center, True)
                    mx = 6
                    if self.i10l:
                        mx = 11
                    if len(self.player.items) == mx:
                        self.player.items.pop(0)
                if go.type == "mine" and not go.dead:
                    kaboom = True
            if (kaboom or go.health <= 0 or go.kaboom) and not go.dead:
                go.dead = True
                go.frame_rate = 1 / 25
                Sound(fix_path("audio/alienExplode.wav")).play()
                cx1, cy1 = self.player.get_rect().center
                cx2, cy2 = go.get_rect().center
                dist = math.hypot(cx1 - cx2, cy1 - cy2)
                damage = ((128 - dist) / 128)
                if damage > 0:
                    if self.player.shield:
                        self.player.shield -= damage / 2
                    else:
                        self.player.health -= damage
                    if self.player.shield < 0:
                        self.player.shield = 0
                    self.add_points(round(-150 * damage), go.get_rect().move(0, -100).center)
                for g in self.GOs:
                    if g.type in ("moneyBag", "mine"):
                        cx1, cy1 = g.get_rect().center
                        cx2, cy2 = go.get_rect().center
                        dist = math.hypot(cx1 - cx2, cy1 - cy2)
                        if dist < 128:
                            if g.type == "moneyBag":
                                g.dead = True
                            if g.type == "mine" and not g.dead:
                                g.kaboom = True
        for alien in self.aliens:
            alien.update(self.time_passed)
            if alien.grounded and self.mission.clean_room:
                self.endgame = "lost"
            if not alien.health in [0, alien.start_health]:
                alien.life_bar = True
            if alien.dead == 2 and alien.health <= 0 and alien.hitBy == "lightning":
                alien.health = 0
                self.doubleDie(alien)
            if alien.health <= 0:
                 if not alien.dead:
                     self.item_progress += alien.__class__.item_value * self.mission.item_mul
                     self.AddKilledAlien()
                     if self.item_progress >= 1:
                         self.item_progress -= 1
                         if self.mission.items_dropped < self.mission.items:
                             self.GOs.append(GameObject((425, 0), self.images, self.mission, "block"))
                             self.mission.items_dropped += 1
                         if self.mission.items_dropped >= self.mission.items:
                             _go = GameObject((425, 0), self.images, self.mission, "moneyBag", amount=1500)
                             _go.health *= 10
                             self.GOs.append(_go)
                     alien.dead = 1
                     points = 0
                     if alien.health == 0:
                         alien.dead = random.randint(1, 2)
                         if alien.dead == 2 and alien.hitBy == "lightning":
                             alien.health = alien.start_health
                     if not alien.hitBy == "lightning":
                         if not alien.health == 0:
                             points += (0 - alien.health) * 5 + ((alien.hitBy.hits - 1) * 10)
                     alien.phase_rate = .05
                     alien.phase = 1
                     if alien.dead == 1:
                         if not random.randint(0, 29):
                             self.add_points("JACKPOT!", alien.get_rect().center, True)
                             MONEYBAGS = 20
                             VELOCITIES = range(-MONEYBAGS // 2, MONEYBAGS // 2)
                             POWER = 50
                             for x in range(MONEYBAGS):
                                 self.GOs.append(GameObject(alien.get_rect().center, self.images, self.mission, velocity=[(VELOCITIES[x] * random.uniform(.8, 1.2) * POWER), -random.uniform(200, 500)],\
                                         type="moneyBag", amount=random.choice([75, 100, 125, 150, 150, 150, 150, 175, 200, 500])))
                         else:
                             self.add_points(alien.death_amount[0] + points, alien.get_rect().center)
                             alien.explode_sound.play()
                     else:
                         alien.death_sound.play()
                         self.add_points(alien.death_amount[1] + points, alien.get_rect().center)
                     continue
            if alien.kill:
                del self.aliens[self.aliens.index(alien)]
                continue
            r1 = self.player.get_rect()
            r2 = pygame.Rect((0, 0), (80, 80))
            r2.center = alien.get_rect().center
            for go in self.GOs:
                if go.get_rect().colliderect(r2) and alien.grounded:
                    if go.type == "moneyBag":
                        go.health -= alien.impact_damage[0]
                    if go.type == "mine":
                        go.dead = True
            if r1.colliderect(r2) and not alien in self.player.hitBy:
                if alien.grounded:
                    if self.player.shield:
                        self.player.shield -= alien.impact_damage[1]
                        if self.player.shield < 0:
                            self.player.shield = 0
                    else:
                        self.player.health -= alien.impact_damage[0]
                    self.player.hitBy.append(alien)
                    self.add_points(-150, alien.get_rect().center)
                if not alien.dead:
                    if self.player.shield:
                        self.player.shield = 0
                        self.AddKilledAlien()
                    else:
                        self.player.health = 0
                    self.add_points(-500, alien.get_rect().center)
                    alien.dead = 1
                    alien.explode_sound.play()
            for laser in self.player.lasers:
                if alien.get_rect().colliderect(laser.get_rect()) and alien.hitBy != laser and not laser.dead and alien.dead != 1:
                    alien.health -= laser.damage
                    if alien.dead == 2 and not alien.grounded:
                        self.doubleDie(alien)
                        self.item_progress += (alien.__class__.item_value / 3) * self.mission.item_mul
                    laser.hits += 1
                    alien.hitBy = laser
                    if alien.health >= 0:
                        laser.die()
        Items = self.player.current_items
        newDict = copy.copy(Items)
        for item in newDict:
            if newDict[item].total_time >= newDict[item].length:
                self.disableItem(item)
        pygame.display.update()
        self.alien_time += self.time_passed
        if self.alien_time >= self.next_alien:
            if not self.ran_out_of_aliens:
                self.aliens.append(self.next_wave.get_alien_type()((0, 0), self.images, self.flaks, self.GOs, self.player, self.mission))
                self.next_wave.completed += 1
                if self.next_wave.completed == self.next_wave.amount:
                    if len(self.mission.patterns):
                        self.next_wave = self.mission.patterns.pop(0)
                    else:
                        self.ran_out_of_aliens = True
            if self.mission.boss == None:
                self.bossed = True
            if self.ran_out_of_aliens and not self.bossed and len(self.aliens) == 0:
                self.bossed = True
                self.aliens.append(self.mission.boss((0, 0), self.images, self.flaks, self.GOs, self.player, self.mission))
            self.alien_time = 0
            if not self.ran_out_of_aliens:
                self.next_alien = random.uniform(*self.next_wave.rate)
        if self.endgame:
            transition(self.Display)
            self.done = True
        self.time_passed = CLOCK.tick(60) / 1000
        if self.notimer:
            self.notimer = False
            self.time_passed = 0

    def doubleDie(self, alien):
        self.add_points(alien.death_amount[2], alien.get_rect().center)
        self.GOs.append(GameObject(alien.get_rect().center, self.images, self.mission, type="moneyBag", amount=alien.death_amount[3]))
        alien.explode_sound.play()
        alien.dead = 1

    def disableItem(self, item):
        Items = self.player.current_items
        if Items[item].name == "Green Laser":
            self.player.fireObject = Laser
            lightning.GREEN_ON = False
        if Items[item].name == "2x Fire Rate":
            self.player.fire_per_sec /= 2
            lightning.MAX_THINGS /= 3
        if Items[item].name == "2x Speed":
            self.player.max_velocity /= 2
        if Items[item].name == "Lightning":
            self.player.canFire = True
        if Items[item].name == "Auto Gun":
            self.player.beam = self.player.always_beam
        if Items[item].name == "Shield Regenerator":
            self.player.regen = False
        if Items[item].name == "Magnet":
            for go in self.GOs:
                go.tracking_speed = constants.ATTRACTION.get(go.type, 0)
        Items.pop(item)

class Flak:
    def __init__(self, images, center, mission, charge, rotation = 0):
        self.rotation = rotation
        self.images = images
        self.mission = mission
        rect = pygame.Rect((0, 0), (128, 128))
        rect.center = center
        self.centerx = center[0]
        self.pos = list(rect.topleft)
        self.time_passed = 0
        amount = (-4000 * charge)
        self.velocity = pygame.Vector2([(cos(radians(rotation + 90)) * amount), (sin(radians(rotation + 90)) * amount)])
        self.dead = False
        self.kill = False
        self.frame = 1
        self.frame_rate = 1 / 25
        self.frame_time = 0
        self.sound = Sound(fix_path("audio/flak.wav"))
        self.first_run = 0
        self.lastDead = False
        self.isBomb = False
        self.hits = 0
        self.image_name = "flak"

    def get_rect(self):
        rect = pygame.Rect((0, 0), (128, 128))
        rect.topleft = self.pos
        rect.centerx = self.centerx
        return rect

    def get_rect2(self):
        rect = pygame.Rect((0, 0), (16, 16))
        rect.center = self.get_rect().center
        return rect

    def draw(self, surf):
        if not self.dead:
            surf.blit(pygame.transform.rotate(self.images[self.image_name], -self.rotation), self.get_rect2())
        if self.dead:
            surf.blit(self.images[f"fireball{self.frame}"], self.get_rect())

    def update(self, time_passed):
        if self.dead:
            self.frame_time += time_passed
            if self.frame_time >= self.frame_rate:
                self.frame_time = 0
                self.frame += 1
                if self.frame >= 61:
                    self.frame = 60
                    self.kill = True
        if self.get_rect2().bottom >= self.mission.ground and self.first_run > 5 and not self.dead:
            self.dead = True
            self.sound.play()
        self.first_run += 1
        if not self.dead:
            if self.centerx < 0:
                self.velocity[0] = abs(self.velocity[0])
            if self.centerx > 800:
                self.velocity[0] = -abs(self.velocity[0])
            self.velocity[1] += (self.mission.planet.gravity * G) * time_passed / METER
            self.centerx += self.velocity[0] * time_passed
            self.pos[0] += self.velocity[0] * time_passed
            self.pos[1] += self.velocity[1] * time_passed

class Bomb(Flak):
    def __init__(self, images, center, mission):
        super().__init__(images, center, mission, 0)
        self.isBomb = True
        self.image_name = "bomb"
        self.hitBy = 0

class Volcano:
    def __init__(self, centerx, images):
        self.images = images
        self.size = (64, 64)
        self.rect = pygame.Rect((0, 0), self.size)
        self.rect.centerx = centerx
        self.rect.bottom = 495 - random.randint(0, 10)
        self.next_erupt_time = (5, 20)
        self.erupt_time = 0
        self.frame = 1
        self.flip = random.randint(0, 1)
        self.next_erupt_set()
        self.erupting = False
        self.frame_time = 0
        self.frame_rate = 1 / 25
    
    def next_erupt_set(self):
        self.next_erupt = random.randint(*self.next_erupt_time)
        
    def draw(self, surf):
        surf.blit(pygame.transform.flip(self.images[f"volcano{self.frame}"], self.flip, 0), self.rect)

    def update(self, time_passed):
        if not self.erupting:
            self.erupt_time += time_passed
        if self.erupt_time >= self.next_erupt:
            self.erupting = True
            self.erupt_time = 0
        if self.erupting:
            self.frame_time += time_passed
            if self.frame_time >= self.frame_rate:
                self.frame += 1
                self.frame_time = 0
            if self.frame == 401:
                self.frame = 1
                self.erupting = False
                self.next_erupt_set()





from ii_game.scripts import menu
from ii_game.scripts import store_data
from ii_game.scripts.inventory import Inventory
