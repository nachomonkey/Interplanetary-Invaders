import pygame
import pygame.gfxdraw
from pygame import Vector2
import sys
import time
import shelve
import copy
import humanize
from math import sin, cos, pi, radians, sqrt, isclose
from ii_game.scripts import saves
from ii_game.scripts.planets import Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune, Pluto, PLANET_BY_NAME, MOONS
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts.maps import AllMaps, MapPoint
from ii_game.scripts.confirm import confirmExit
from ii_game.scripts.transition import transition
from ii_game.scripts.menu import build_bar
from ii_game.scripts import screenshot
from ii_game.scripts.pause_menu import pause_menu
from ii_game.scripts.stores import StoreUI
from ii_game.scripts.utils import colorize, fix_path
from ii_game.scripts.get_file import get_file
from ii_game.scripts import joystick

pygame.init()

clock = pygame.time.Clock()

TIME_WARP = 10000

HOUR = 60 * 60

DAY = HOUR * 24

class SpaceMap:
    def __init__(self, images, display, profile, profile_number, focus = "theSun"):
        self.images = images
        self.Display = display
        self.display = pygame.Surface((800, 600))
        self.done = False
        self.time_passed = 0
        self.planets1 = [Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune]
        for planet in MOONS:
            for moon in MOONS[planet]:
                self.planets1.append(moon)
        self.planets1.reverse()
        self.planets = []
        for p in self.planets1:
            self.planets.append(p())
        self.sunRect = pygame.Rect(0, 0, 20, 20)
        self.sunRect.center = self.Display.get_rect().center
        self.real_world_time = 0
        self.offset = [0, 0]
        self.target_offset = [0, 0]
        self.zoom = 1
        self.target_zoom = 1.5
        self.scroll_speed = 300
        self.scroll_range = 10
        self.zoom_amount = .1
        self.focused = None
        self.sun_frame = 1
        self.next_sun_frame = 0
        self.sun_frame_len = 1 / 25
        self.overlay_pos = None
        self.moving_start = 0
        self.moving = False
        if focus in PLANET_BY_NAME:
            focus = self.planets1.index(PLANET_BY_NAME[focus])
        self.focused = focus
        self.mouse_on = False
        self.profile = profile
        self.profile_number = profile_number
        self.money = self.profile["money"]
        self.text_yellow = False
        self.text_rate = 1 / 5
        self.text_time = 0
        self.start_click = None
        self.last_sample = None
        unlocked_planets = self.profile["unlocked_planets"]
        self.unlocked_planets = []
        for u in unlocked_planets:
            for p in self.planets:
                if isinstance(p, PLANET_BY_NAME[u]):
                    self.unlocked_planets.append(p)
        self.missions_left = {}
        for planet in self.unlocked_planets:
            self.missions_left[planet.name] = 0
            try:
                for p in self.profile["map"][planet.name]:
                    if p.alien_flag:
                        self.missions_left[planet.name] += 1
            except KeyError:
                print(colorize(f"No map for {planet.name} found!", "fail"))
        self.speed = 1
        pygame.mixer.music.load(fix_path(get_file("audio/music/AmbientSpace.mp3")))
        pygame.mixer.music.play(-1)
#        pygame.display.toggle_fullscreen()

    def main(self):
        joystick.Reset()
        while not self.done:
            self.events()
            self.draw()
            self.update()
        pygame.mixer.music.fadeout(1000)
        transition(self.Display, 5)
        joystick.Reset()
        return self.profile

    def events(self):
        for event in pygame.event.get():
            joystick.Update(event)
            click = False
            if event.type == pygame.QUIT:
                confirmExit(self.Display, self.profile, self.profile_number)
            if event.type == pygame.MOUSEBUTTONDOWN and not self.focused in ("theSun", None):
                planet = self.planets[self.focused]
                rect = pygame.Rect((0, 0), (205, 50))
                rect.midtop = planet.center[1][0], planet.center[1][1] + 35
                if rect.collidepoint(pygame.mouse.get_pos()):
                    click = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.start_click = pygame.math.Vector2(pygame.mouse.get_pos())
                self.last_sample = copy.copy(self.start_click)
                if pygame.Rect(0, 0, 32, 32).collidepoint(pygame.mouse.get_pos()):
                    self.done = True
                rect = pygame.Rect(0, 0, 32, 32)
                rect.midright = self.Display.get_rect().midright
                if rect.collidepoint(pygame.mouse.get_pos()):
                    for e, p in enumerate(self.planets):
                        if p.name == "Earth":
                            self.focused = e
            if event.type == pygame.MOUSEBUTTONUP:
                self.start_click = None
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                if not hasattr(event, 'key'):
                    event.key = None
                if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                    self.done = True
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or joystick.GoEvent():
                    click = True
                if event.key == pygame.K_LEFT or joystick.JustWentLeft():
                    self.speed -= .1
                    if self.speed < 0:
                        self.speed = 0
                if event.key == pygame.K_RIGHT or joystick.JustWentRight():
                    self.speed += .1
                    if self.speed > 2:
                        self.speed = 2
                if event.key == pygame.K_F2 or joystick.JustPressedLB():
                    screenshot.capture(self.profile_number, self.Display)
                if event.key == pygame.K_COMMA or joystick.JustPressedLT():
                    if self.focused == None:
                        self.focused = 0
                    self.focused = (self.focused + 1) % len(self.planets)
                    self.target_zoom = 1.5
                if event.key == pygame.K_PERIOD or joystick.JustPressedRT():
                    if self.focused == None:
                        self.focused = 0
                    self.focused = (self.focused - 1) % len(self.planets)
                    self.target_zoom = 1.5
            if event.type == pygame.MOUSEMOTION:
                self.mouse_on = True
            if event.type == pygame.MOUSEBUTTONUP:
                pos = pygame.mouse.get_pos()
                nto = self.target_offset[:]
                if event.button == 5:
                    self.target_zoom -= self.zoom_amount
                    nto[0] -= (pos[0] - self.Display.get_width() / 2) / 10
                    nto[1] -= (pos[1] - self.Display.get_height() / 2) / 10
                if event.button == 4:
                    self.target_zoom += self.zoom_amount
                    nto[0] += (pos[0] - self.Display.get_width() / 2) / 10
                    nto[1] += (pos[1] - self.Display.get_height() / 2) / 10
                if self.target_zoom < .5:
                   self.target_zoom = .5
                elif self.target_zoom > 2:
                    self.target_zoom = 2
                else:
                    self.target_offset = nto
            if not self.focused in ("theSun", None) and self.zoom >= 1.25 and click and self.planets[self.focused] in self.unlocked_planets:
                self.profile["planet"] = self.planets[self.focused]
                self.done = True

    def blit(self, img, dest, offset = 1):
        self.display.blit(img, (dest[0] - self.offset[0] * offset, dest[1] - self.offset[1] * offset))

    def circle(self, surf, color, center, radius, width = 0):
        pygame.draw.circle(surf, color, (round(center[0] - self.offset[0]), round(center[1] - self.offset[1])), round(radius), width)

    def retro_text(self, *args, **kwargs):
        args = list(args)
        pos = list(args.pop(0))
        pos[0] -= self.offset[0]
        pos[1] -= self.offset[1]
        retro_text(pos, *args, **kwargs)

    def getCursorPos(self, afz = True):
        pos = list(pygame.mouse.get_pos())
        pos[0] += self.offset[0]
        pos[1] += self.offset[1]
        if afz:
            pos[0] /= self.zoom
            pos[1] /= self.zoom
        return pos

    def adjustForZoom(self, pos, mul = False):
        pos = list(pos)
        z = self.zoom
        if mul:
            z = 1 / z
        pos[0] /= z
        pos[1] /= z
        return pos

    def adjustForOffset(self, pos):
        pos = list(pos)
        pos[0] -= self.offset[0]
        pos[1] -= self.offset[1]
        return pos

    def draw(self):
        pos = pygame.mouse.get_pos()
        self.display = pygame.Surface((800 / self.zoom, 600 / self.zoom))
        self.blit(self.images["background_large"], (0, 0), 0.01)
        self.blit(self.images["stars"], (-600, -800), .5)
        self.blit(pygame.transform.flip(self.images["stars"], 0, 1), (-600, -800), .7)
        self.blit(pygame.transform.scale(self.images[f"spinningSun{self.sun_frame}"], (20, 20)), self.sunRect)
        found_col = False
        for planet in self.planets:
            hasAnim = True
            rgba = ""
            if planet.isMoon:
                if planet.rgba:
                    rgba = "RGBA"
            if not f"spinning{planet.name}{rgba}1" in self.images:
                hasAnim = False
            center = self.sunRect.center
            offset = [0, 0]
            div = 1
            draw = True
            if planet.isMoon:
                draw = False
                div = (1609.344 * 10 ** 4) / 1.5
                for p in self.planets:
                    if p.name == planet.parent:
                        if self.focused:
                            if self.planets[self.focused].name == p.name:
                                draw = True
                            else:
                                for m in MOONS[p.name]:
                                    if self.planets[self.focused].name == m.name:
                                        draw = True
                        parent = planet
                        offset = pygame.math.Vector2(p.center[0]) - pygame.math.Vector2(center)
            planet.draw = draw
            orbit_color = (255, 125, 125)
            if planet in self.unlocked_planets:
                orbit_color = (255, 255, 255)
            if not planet.name in ("Uranus", "Neptune") and draw:    # AA circles don't work with extreme diameters
                try:
                    pygame.gfxdraw.aacircle(self.display, round(center[0] - self.offset[0] + offset[0]), round(center[1] - self.offset[1] + offset[1]), round(planet.distance / div), orbit_color)
                except OverflowError:
                    self.focused = "theSun"
            else:
                if draw:
                    self.circle(self.display, orbit_color, center, round(planet.distance), 1)
            rect = pygame.Rect(0, 0, 10, 10)
            if hasAnim or f"still_{planet.name.lower()}" in self.images:
                rect = pygame.Rect(0, 0, 20, 20)
            P = planet
            x = sin(radians(P.position)) * round(P.distance / div)
            y = cos(radians(P.position)) * round(P.distance / div)
            rect.centerx = self.sunRect.centerx + x + offset[0]
            rect.centery = self.sunRect.centery + y + offset[1]
            rect2 = rect.copy()
            rect2.size = self.adjustForZoom(rect2.size, True)
            rect2.topleft = self.adjustForZoom(self.adjustForOffset(rect2.topleft), True)
            if rect2.collidepoint(pos):
                self.overlay_pos = [rect.center, rect2.center, planet]
                found_col = True
            if not hasAnim and draw and f"still_{planet.name.lower()}" in self.images:
                self.blit(pygame.transform.scale(self.images[f"still_{planet.name.lower()}"], (20, 20)), rect)
            elif not hasAnim and draw:
                size = 10
                if planet.isMoon:
                    size = 5
                self.circle(self.display, planet.color, (rect.center[0], rect.center[1]), size)
            elif draw:
                rot = planet.rotation
                if not planet.rotational_period:
                    rot = planet.position
                    if planet.name == "Deimos":
                        pass
                frame = round(25 * (rot % 360 / 360)) + 1
                if 25 < frame:
                    frame = 1
                self.blit(pygame.transform.scale(self.images[f"spinning{planet.name}{rgba}{frame}"], (20, 20)), rect)
            self.planets[self.planets.index(planet)].position += 100 / planet.orbital_period * self.time_passed * 10
            if planet.rotational_period:
                self.planets[self.planets.index(planet)].rotation += 10000 / planet.rotational_period  * self.time_passed
            self.planets[self.planets.index(planet)].center = (rect.center, rect2.center)
        if not found_col:
            self.overlay_pos = None

    def drawOverlays(self):
        self.Display.blit(self.images["backarrow"], (0, 0))
        rect = pygame.Rect(0, 0, 32, 32)
        rect.midright = self.Display.get_rect().midright
        self.Display.blit(self.images["recenter"], rect)
        build_bar(self.Display, (400, 30), self.speed / 2, startmark = "0x", endmark = "2x")
        retro_text(self.Display.get_rect().topright, self.Display, 20, f"Cash: {humanize.intcomma(int(self.money))}", font = "impact", anchor = "topright")
        if self.overlay_pos != None and self.overlay_pos[2].draw:
            tpos = list(self.overlay_pos[1])
            tpos[1] -= 50
            retro_text(tpos, self.Display, 20, self.overlay_pos[2].name, font = "Sans")
        if not self.focused in ("theSun", None) and self.zoom >= 1.25:
            planet = self.planets[self.focused]
            if planet in self.unlocked_planets:
                rect2 = pygame.Rect((0, 0), (205, 50))
                rect2.midtop = planet.center[1][0], planet.center[1][1] + 35
                color = (100, 100, 100)
                if pygame.key.get_pressed()[pygame.K_RETURN] or rect2.collidepoint(pygame.mouse.get_pos()):
                    color = (70, 70, 70)
                pygame.draw.rect(self.Display, (0, 0, 0), rect2.move(3, 3))
                pygame.draw.rect(self.Display, color, rect2)
                color = (255, 255, 255)
                if self.text_yellow:
                     color = (255, 255, 0)
                retro_text(rect2.center, self.Display, 14, f"Go To {planet.name}", color=color, anchor="center")
            rect = pygame.Rect((0, 0), (250, 300))
            rect.midright = self.Display.get_rect().midright
            if self.zoom < 1.5:
                rect.x += rect.w * ((1.5 - self.zoom) / .25)
            pygame.draw.rect(self.Display, (25, 25, 25), rect)
            retro_text(rect.midtop, self.Display, 20, planet.name, font = "Sans", anchor = "midtop")
            pos = [rect.left + 10, rect.top + 25]
            height = 12
            pressure = planet.surface_pressure
            if pressure == None:
                pressure = "Unknown"
            ml = ""
            rot_per = planet.rotational_period
            if not rot_per:
                rot_per = "Synchronous"
            if planet.name in self.missions_left:
                ml = f"Missions: {self.missions_left[planet.name]}"
            text = f"""Gravity: {planet.gravity} G
Rotational Period: {rot_per} hours
Year Length: {planet.orbital_period} days
AvgDistFromSun: {planet.distance * 1000000} mi.
Rotation: {round(planet.rotation % 360, 2)}
Surface Pressure: {pressure} {'atm.' if pressure != 'Unknown' else ''}
{ml}
Targetable Moons: {planet.moons}"""
            if not planet in self.unlocked_planets:
                text = "LOCKED"
            for line in text.split("\n"):
                retro_text(pos, self.Display, height, line, font = "Sans", anchor = "topleft", res = 10, smooth = True)
                pos[1] += height
#        retro_text(self.Display.get_rect().midtop, self.Display, 20, f"PLANETS ARE NOT ACTUAL SIZE", font = "ubuntu", anchor = "midtop")

    def update(self):
        mPos = pygame.mouse.get_pos()
        pressed = pygame.mouse.get_pressed()
        kpressed = pygame.key.get_pressed()
        self.oldMoving = self.moving
        self.moving = False
        if self.start_click:
            to = pygame.math.Vector2(self.target_offset)
            to -= (pygame.math.Vector2(pygame.mouse.get_pos()) - self.last_sample)
            self.last_sample = pygame.math.Vector2(pygame.mouse.get_pos())
            self.target_offset = to
            self.moving = True
        for planet in self.planets:
            rect = pygame.Rect((0, 0), self.adjustForZoom((20, 20), True))
            rect.center = planet.center[1]
            if rect.collidepoint(mPos) and pressed[0] and planet.draw:
                self.focused = self.planets.index(planet)
                self.target_zoom = 2
        if kpressed[pygame.K_LEFT] or kpressed[pygame.K_RIGHT] or kpressed[pygame.K_UP] or kpressed[pygame.K_DOWN]:
            self.mouse_on  = True
        if self.mouse_on and not self.start_click:
            if mPos[0] < self.scroll_range or kpressed[pygame.K_LEFT]:
                self.target_offset[0] -= self.scroll_speed * (self.time_passed / self.speed)
                self.moving = True
            if mPos[0] > self.Display.get_width() - self.scroll_range or kpressed[pygame.K_RIGHT]:
                self.target_offset[0] += self.scroll_speed * (self.time_passed / self.speed)
                self.moving = True
            if mPos[1] < self.scroll_range or kpressed[pygame.K_UP]:
               self.target_offset[1] -= self.scroll_speed * (self.time_passed / self.speed)
               self.moving = True
            if mPos[1] > self.Display.get_height() - 50 or kpressed[pygame.K_DOWN]:
                self.target_offset[1] += self.scroll_speed * (self.time_passed / self.speed)
                self.moving = True
        if self.moving and not self.oldMoving:
            self.moving_start = time.time()
        self.offset[0] -= (self.offset[0] - self.target_offset[0]) / 10
        self.offset[1] -= (self.offset[1] - self.target_offset[1]) / 10
        self.offset = [round(self.offset[0]), round(self.offset[1])]
        self.zoom -= (self.zoom - self.target_zoom) / 10
        if self.focused != None:
            if self.focused != "theSun":
                target = list(self.planets[self.focused].center[0])
            else:
                target = list(self.sunRect.center)
            target[0] -= (self.Display.get_width() / 2) / self.zoom
            target[1] -= (self.Display.get_height() / 2) / self.zoom
            self.target_offset = target
            if self.target_zoom <= .7 or (self.moving and time.time() - self.moving_start >= .25):
                self.focused = None
        self.display.set_clip(pygame.Rect(0, 0, 800 // self.zoom, 600 // self.zoom))
        self.Display.fill((0, 0, 0))
        try:
            self.Display.blit(pygame.transform.smoothscale(self.display, (round(self.display.get_width() * self.zoom), round(self.display.get_height() * self.zoom))), (0, 0))
        except ValueError:
            self.zoom += self.zoom_amount
        self.drawOverlays()
        pygame.display.update()
        self.time_passed = ((clock.tick(60) / 1000) / 3) * self.speed
        self.next_sun_frame += self.time_passed
        if self.sun_frame_len <= self.next_sun_frame:
            self.sun_frame += 1
            self.next_sun_frame = 0
        if self.sun_frame > 25:
            self.sun_frame = 1
        self.text_time += self.time_passed
        if self.text_time >= self.text_rate:
            self.text_yellow = not self.text_yellow
            self.text_time = 0


class Map:
    def __init__(self, images, display, profile, profile_number, point = None):
        self.images = images
        self.display = display
        self.profile = profile
        self.done = False
        self.planet = profile["planet"]
        self.time_passed = 0
        try:
            self.map = profile["map"][self.planet.name]
        except:
            self.map = [MapPoint((400, 300), "Landing Zone", type=None), MapPoint((450, 300), f"Spaceport {self.planet.name}", type="spaceport")]
        if point == None:
            point = profile["points"][self.planet.name]
            if point >= len(self.map):
                point = len(self.map) - 1
        self.selected_point = point
        self.old_selected_point = point
        self.avatar_frame = 1
        self.frame_rate = 1 / 4
        self.frame_time = 0
        self.avatar_frames = 2
        self.avatar_idle_frame = 1
        self.idle_frame_rate = 1
        self.idle_frame_time = 0
        self.avatar_pos = self.get_point(self.selected_point)
        self.target_pos = copy.copy(self.avatar_pos)
        self.target_pos = self.get_point(point)
        self.set_velocity()
        self.waypoints = []
        self.clock = pygame.time.Clock()
        self.text_yellow = False
        self.text_rate = 1 / 5
        self.text_time = 0
        self.profile_number = profile_number
        self.toMenu = False
        self.base_rect = pygame.Rect(0, 0, 300, 50)
        self.base_rect.midbottom = display.get_rect().midbottom
        self.prev_dist = self.get_dist(self.avatar_pos, self.target_pos)
        self.pause_time = False
        self.ForwardOrBack = False
        self.ForwardOrBack2 = False
        self.click = False
        self.last_hit_point = point

    def set_velocity(self):
        diff = self.avatar_pos - self.target_pos
        while abs(diff[0]) > 220 or abs(diff[1]) > 220:
            diff /= 1.05
        self.velocity = diff

    def get_point(self, index):
        try:
            return pygame.math.Vector2(self.map[index].rect.move(20, 55).topleft)
        except IndexError:
            return self.get_point(len(self.map) - 1)

    def main(self):
        joystick.Reset()
        while not self.done:
            self.events()
            self.draw()
            self.update()
        transition(self.display, 5)
        joystick.Reset()
        return self.map[self.selected_point].mission, self.selected_point

    def GetDestDirection(self, p1, p2):  # 0 = up, 1 = right, 2 = down, 3 = left
        P1 = self.get_point(p1)
        P2 = self.get_point(p2)
        angle = pygame.math.Vector2().angle_to(P1 - P2)
#        angle = P1.angle_to(P2)
        angle %= 360
        if isclose(angle, 270, abs_tol = 45):
            return 0
        if isclose(angle, 0, abs_tol = 45):
            return 3
        if isclose(angle, 360, abs_tol = 45):
            return 3
        if isclose(angle, 90, abs_tol = 45):
            return 2
        if isclose(angle, 180, abs_tol = 45):
            return 1

    def GetInputDirection(self, event):
        if event.key == pygame.K_UP or joystick.JustWentUp():
            return 0
        if event.key == pygame.K_LEFT or joystick.JustWentLeft():
            return 1
        if event.key == pygame.K_DOWN or joystick.JustWentDown():
            return 2
        if event.key == pygame.K_RIGHT or joystick.JustWentRight():
            return 3

    def RelCalc(self):
        a

    def GoForwardOrBack(self, event, rel=False):
        IsForward = False
        IsBack = False
        sel = self.selected_point
        if sel > 0:  # Check back
            if self.GetDestDirection(sel - 1, sel) == self.GetInputDirection(event):
                IsBack = True
        if sel < len(self.map) and not self.map[sel].alien_flag:
            if self.GetDestDirection(sel + 1, sel) == self.GetInputDirection(event):
                IsForward = True
        if IsBack and IsForward:
            return self.ForwardOrBack and self.ForwardOrBack2
        if IsBack:
            return False
        if IsForward:
            return True

    def events(self):
        for event in pygame.event.get():
            joystick.Update(event)
            click = False
            if event.type == pygame.QUIT:
                confirmExit(self.display, self.profile, self.profile_number)
                self.pause_time = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                sel = self.selected_point
                rect = pygame.Rect((0, 0), (220, 50))
                rect.midtop = self.map[sel].pos[0], self.map[sel].pos[1] + 35
                backrect = pygame.Rect(0, 0, 32, 32)
                if rect.collidepoint(pygame.mouse.get_pos()):
                    click = True
                elif backrect.collidepoint(pygame.mouse.get_pos()):
                    self.toMenu = True
                    self.done = True
                self.click = True
            if not hasattr(event, "key"):
                event.key = None
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                if event.key == pygame.K_F2 or joystick.JustPressedLB():
                    screenshot.capture(self.profile_number, self.display)
                    self.pause_time = True
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or joystick.GoEvent():
                    click = True
                if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                    tmm = pause_menu(self.display, self.images, self.profile, self.profile_number)
                    self.pause_time = True
                    if tmm:
                        self.toMenu = True
                        self.done = True
            if event.type == pygame.KEYUP or joystick.WasEvent():
                tabbed = False
                sel = self.selected_point
                if (event.key == pygame.K_TAB) and not self.map[self.selected_point].alien_flag:
                    sel += 1
                    tabbed = True
                FB = self.GoForwardOrBack(event)
                if (FB):
                    sel += 1
                if (FB == False):
                    sel -= 1
#                if (event.key == pygame.K_LEFT or joystick.JustWentLeft()):
#                    sel -= 1
#                if (event.key == pygame.K_RIGHT or joystick.JustWentRight()) and not self.map[self.selected_point].alien_flag:
#                    sel += 1
                if (event.key == pygame.K_END or joystick.JustPressedRT()):
                    self.waypoints = []
                    x = 0
                    for x in range(self.selected_point, len(self.map)):
                        self.waypoints.append(x)
                        if self.map[x].alien_flag:
                            break
                    sel = x
                    if self.waypoints:
                        self.target_pos = self.get_point(self.waypoints[0])
                if (event.key == pygame.K_HOME or joystick.JustPressedLT()):
                    self.waypoints = []
                    x = 0
                    for x in reversed(range(self.selected_point)):
                        self.waypoints.append(x)
                        if self.map[x].alien_flag:
                            break
                    sel = x
                    if self.waypoints:
                        self.target_pos = self.get_point(self.waypoints[0])
                self.selected_point = sel
                if self.target_pos != self.avatar_pos:
                    self.waypoints.append(sel)
                if self.selected_point < 0:
                    self.selected_point = 0
                yes = False
                if self.waypoints:
                    if self.waypoints[-1] >= len(self.map):
                        yes = True
                if self.selected_point >= len(self.map) or yes:
                    if yes:
                        self.waypoints[-1] = len(self.map) - 1
                    if tabbed and not yes:
                        self.selected_point = 0
                        self.waypoints += list(reversed(range(len(self.map))))
                        for x in reversed(range(len(self.map))):
                            if x > 0:
                                if self.map[x - 1].alien_flag:
                                    break
                            self.waypoints.append(x)
                    else:
                        self.selected_point = len(self.map) - 1
            if self.target_pos == self.avatar_pos and click:
                t = self.map[self.selected_point].type
                if t == "spaceport":
                    spacemap = SpaceMap(self.images, self.display, self.profile, self.profile_number, focus = self.planet.name)
                    transition(self.display, 5)
                    self.profile = spacemap.main()
                    self.__init__(self.images, self.display, self.profile, self.profile_number)
                if t == "mission":
                    self.done = True
                if t == "store":
                    sel1 = self.selected_point
                    store = StoreUI(self.display, self.images, self.profile, self.profile_number, self.map[self.selected_point])
                    if store.main():
                        self.waypoints = []
                        self.target_pos = self.get_point(0)
                        self.avatar_pos = self.get_point(0)
                        self.set_velocity()
                        self.selected_point = 0

    def draw(self):
        if f"map_{self.planet.name}" in self.images:
            self.display.blit(self.images[f"map_{self.planet.name}"], (0, 0))
        else:
            self.display.fill(self.planet.color)
        self.display.blit(self.images["backarrow"], (0, 0))
        dark = False
        d1 = self.images["empty"].copy()
        d2 = self.images["empty"].copy()
        pygame.draw.rect(self.display, (25, 25, 25), self.base_rect)
        retro_text(self.base_rect.center, self.display, 15, f'Loot: {self.profile["money"]}', anchor="center")
        for n, point in enumerate(self.map):
            circle = self.images["nothing16"]
            circle_rect = circle.get_rect()
            circle_rect.center = point.pos
            circle_rect2 = pygame.Rect(0, 0, 64, 80)
            circle_rect2.midbottom = circle_rect.midbottom
            hover = circle_rect2.collidepoint(pygame.mouse.get_pos())
            color = (255, 0, 0)
            if hover:
                color = (255, 150, 0)
            name = "alien"
            if not point.alien_flag:
                color = (0, 125, 255)
                if hover:
                    color = (255, 255, 255)
                name = "tank"
            if point.type == "spaceport":
                color = (125, 125, 125)
                if hover:
                    color = (125, 255, 255)
                name = "spaceport"
            if point.type == "info":
                color = (0, 0, 255)
                if hover:
                    color = (0, 255, 255)
                name = "info"
            if point.type == "store":
                color = (255, 200, 0)
                if hover:
                    color = (255, 255, 0)
                name = "store"
            try:
                if point.bonus and point.alien_flag:
                    name = "bonus"
            except AttributeError:
                pass
            pygame.draw.ellipse(circle, color, pygame.Rect(circle.get_rect().topleft, (point.rect.w // 4, point.rect.h // 4 * .8)), 2)
            if n > 0:
                if self.map[n - 1].alien_flag:
                    dark = True
                color = (255, 255, 0)
                if dark:
                    color = (150, 150, 20)
                pygame.draw.line(d1, color, point.pos, self.map[n - 1].pos)
            d2.blit(circle, circle_rect)
            d2.blit(self.images[f"{name}_flag{point.frame}"], point.rect)
            if hover and self.click:
                R = []
                if n < self.selected_point:
                    R = reversed(range(self.selected_point))
                if n > self.selected_point:
                    R = range(self.selected_point, len(self.map))
                x = 0
                self.waypoints = []
                for x in R:
                    self.waypoints.append(x)
                    if self.map[x].alien_flag or x == n:
                        break
                self.selected_point = x
                if self.waypoints:
                    self.target_pos = self.get_point(self.waypoints[0])
                self.click = False
        self.display.blit(d1, (0, 0))
        self.display.blit(d2, (0, 0))
        name = ''
        frame = self.avatar_idle_frame
        if self.avatar_pos != self.target_pos:
            name = "_moving"
            frame = self.avatar_frame
        flip = False
        if self.velocity[0] > 0:
            flip = True
        sel = self.selected_point
        self.display.blit(pygame.transform.flip(pygame.transform.scale(self.images[f"tank{name}{frame}"], (32, 32)), flip, False), Vector2(self.avatar_pos) - Vector2(0, 20))
        if self.avatar_pos == self.target_pos and self.old_selected_point == self.selected_point:
                add = ""
                try:
                    if self.map[sel].bonus:
                        add = "Bonus Mission: "
                except AttributeError:
                    pass
                retro_text((self.map[sel].pos[0] + 2, self.map[sel].pos[1] + 2), self.display, 15, add + self.map[sel].name, anchor="midtop", color=(0, 0, 0))
                retro_text((self.map[sel].pos), self.display, 15, add + self.map[sel].name, anchor="midtop")
                if self.map[sel].type in ("spaceport", "mission", "store"):
                    text = "Complete Mission"
                    if self.map[sel].type == "spaceport":
                        text = "Go To Space"
                    if self.map[sel].type == "store":
                        text = "Go To Store"
                    rect = pygame.Rect((0, 0), (220, 50))
                    rect.midtop = self.map[sel].pos[0], self.map[sel].pos[1] + 35
                    color = (100, 100, 100)
                    if pygame.key.get_pressed()[pygame.K_RETURN] or rect.collidepoint(pygame.mouse.get_pos()):
                        color = (70, 70, 70)
                    pygame.draw.rect(self.display, (0, 0, 0), rect.move(3, 3))
                    pygame.draw.rect(self.display, color, rect)
                    color = (255, 255, 255)
                    if self.text_yellow:
                        color = (255, 255, 0)
                    retro_text(rect.center, self.display, 14, text, color=color, anchor="center")

    def get_dist(self, p1, p2):
        return sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def update(self):
        self.click = False
        if (self.prev_dist < self.get_dist(self.avatar_pos, self.target_pos)):
            self.set_velocity()
        self.prev_dist = self.get_dist(self.avatar_pos, self.target_pos)
        if self.old_selected_point != self.selected_point and self.avatar_pos == self.target_pos:
            self.profile["points"][self.planet.name] = self.selected_point
            if not self.waypoints:
                p = self.selected_point
            else:
                p = self.waypoints.pop(0)
            self.target_pos = self.get_point(p)
            self.set_velocity()
            self.last_hit_point = p
            self.selected_point = p
        self.old_selected_point = self.selected_point
        self.avatar_pos -= self.velocity * self.time_passed
        if (round(self.avatar_pos[0] / 6), round(self.avatar_pos[1] / 6)) == (round(self.target_pos[0] / 6), round(self.target_pos[1] / 6)):
            self.avatar_pos = self.target_pos
            if not self.waypoints:
                self.velocity = pygame.math.Vector2()
            else:
                point = self.waypoints.pop(0)
                self.target_pos = self.get_point(point)
                self.selected_point = point
                self.set_velocity()
        else:
            diff = self.avatar_pos - self.target_pos
        for point in self.map:
            point.frame_time += self.time_passed
            if point.frame_time >= point.frame_rate and self.planet.surface_pressure != 0:
                point.frame += 1
                point.frame_time = 0
            if point.frame > point.max_frame:
                point.frame = 1
        self.frame_time += self.time_passed
        self.idle_frame_time += self.time_passed
        if self.frame_time >= self.frame_rate:
            self.avatar_frame += 1
            self.frame_time = 0
        if self.avatar_frame > self.avatar_frames:
            self.avatar_frame = 1
        if self.idle_frame_time >= self.idle_frame_rate:
            self.avatar_idle_frame += 1
            self.idle_frame_time = 0
        if self.avatar_idle_frame > 2:
            self.avatar_idle_frame = 1 
        self.text_time += self.time_passed
        if self.text_time >= self.text_rate:
            self.text_yellow = not self.text_yellow
            self.text_time = 0
        pygame.display.update()
        t = self.clock.tick(60) / 1000
        if not self.pause_time:
            self.time_passed = t
        else:
            self.pause_time = False
