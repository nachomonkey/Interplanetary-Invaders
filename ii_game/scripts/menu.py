import pygame
import os
import shelve
import sys
pygame.init()

clock = pygame.time.Clock()

LOGO_SIZE = (400, 200)

from ii_game.scripts import stars
stars.SIZE = (600, 600)

def build_bar(surf, pos, linepos, subticks = 8, width = 100, height = 25, startmark = "OFF", endmark = "ON"):
    startmark += " "
    endmark = " " + endmark
    rect = pygame.Rect(pos, (width, height))
    pygame.draw.line(surf, (255, 255, 255), rect.midleft, rect.midright, 2)
    pygame.draw.line(surf, (255, 255, 255), rect.topleft, rect.bottomleft, 2)
    pygame.draw.line(surf, (255, 255, 255), rect.topright, rect.bottomright, 2)
    retro_text(rect.midleft, surf, 12, startmark, anchor = "midright")
    retro_text(rect.midright, surf, 12, endmark, anchor = "midleft")
    for z in range(1, subticks + 1):
        x = pos[0] + width * (z / (subticks + 1))
        top = pos[1] + height * 0.2
        bottom = pos[1] + height * 0.8
        pygame.draw.line(surf, (255, 255, 255), (x, top), (x, bottom))
    for z in range(9):
        x = pos[0] + width * linepos
        top = pos[1] + height * 0.2
        bottom = pos[1] + height * 0.8
        v1 = 255 - (abs(z - 4) / 4) * 255
        v2 = z - 4
        pygame.draw.line(surf, (v1, v1, v1), (x + v2, top), (x + v2, bottom))
    cx = pos[0] + width * linepos
    cy = rect.centery + 10
    pygame.draw.polygon(surf, (255, 255, 255), [(cx - 4, cy + 6), (cx, cy + 1), (cx + 4, cy + 6)])

from ii_game.scripts import saves
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts.credits import run_credits
from ii_game.scripts.transition import transition
from ii_game.scripts.utils import fix_path, colorize
from ii_game.scripts import joystick
from ii_game.scripts import screenshot
from ii_game.scripts.get_file import get_file
from ii_game import __version__

class Menu:
    def __init__(self, display, images, options = False, simple = False):
        self.images = images
        self.display = display
        self.options_lock = options
        if options:
            self.background = display.copy()
        try:
            screenshot_count = len(os.listdir(fix_path(get_file("data/screenshots"))))
        except FileNotFoundError:
            screenshot_count = 0
        s = "s"
        if screenshot_count == 1:
            s = ""
        self.options = ["Volume", "Cache Screenshots", f"Delete {screenshot_count} Screenshot{s}", "Stretch to Fullscreen", "Save", "Cancel"]
        self.DEL = f"Delete {screenshot_count} Screenshot{s}"
        self.options_dict = saves.load_options()
        self.profiles = ["Profile #1", "Profile #2", "Profile #3", "Profile #4", "Profile #5", "Back"]
        self.profile_selected = 0
        self.pause_motion = False
        for e, p in enumerate(self.profiles[:-1]):
            if saves.load_profile(e)["new"]:
                self.profiles[e] = f"New Profile #{e + 1}"
        if simple:
            return
        if not options:
            if not os.path.exists(fix_path(get_file("data/menuStarsCache"))):
                for x in range(300):
                    stars.main()
                with shelve.open(fix_path(get_file("data/menuStarsCache"))) as data:
                    data["stars"] = stars.stars
            else:
                with shelve.open(fix_path(get_file("data/menuStarsCache"))) as data:
                    stars.stars = data["stars"]
                pygame.mixer.music.stop()
                pygame.mixer.music.load(fix_path(get_file("audio/music/MainMenu.mp3")))
                pygame.mixer.music.play(-1)
        self.frame = 1
        self.frame_rate = 1 / 120
        self.frame_time = 0
        self.finished = False
        self.time_passed = 0
        self.star_rotation = 0
        self.rotation_speed = 20
        self.done = False
        self.item_selected = 0 
        self.items = ["Play", "Options", "Credits", "Quit"]
        self.play_mode = False
        self.options_mode = options
        self.option_selected = 0
        self.text_time = 0
        self.text_rate = 0.1
        self.text = "Interplanetary Invaders"
        self.bool_images = [self.images["x"], self.images["check"]]

    def main(self):
        while not self.done:
            self.events()
            self.draw()
            self.update()
        if not self.options_lock:
            pygame.mixer.music.fadeout(1000)
            transition(self.display, 5)

    def events(self):
        for event in pygame.event.get():
            joystick.Update(event)
            if event.type == pygame.QUIT:
                self.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not self.finished and not self.options_lock:
                    self.finished = True
                    print(colorize(self.text, 'bold'))
                    self.text = ""
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                if not hasattr(event, "key"):
                    event.key = None
                if event.key == pygame.K_F2 or joystick.JustPressedLB():
                    screenshot.capture("M", self.display)
                if not self.finished and not self.options_lock:
                    self.finished = True
                    print(colorize(self.text, 'bold'))
                    self.text = ""
                else:
                    item = self.item_selected
                    items = self.items
                    if self.options_mode:
                        item = self.option_selected
                        items = self.options
                    if self.play_mode:
                        item = self.profile_selected
                        items = self.profiles
                    if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                        if self.play_mode:
                            self.play_mode = False
                        elif self.options_mode:
                            self.options_mode = False
                            self.options_dict = saves.load_options()
                        else:
                            self.exit()
                    if event.key == pygame.K_UP or joystick.JustWentUp():
                        item -= 1
                    if (event.key == pygame.K_DOWN) or joystick.JustWentDown():
                        item += 1
                    if item < 0:
                        item = 0
                    if item >= len(items):
                        item = len(items) - 1
                    if self.options_mode:
                        self.option_selected = item
                    if self.play_mode:
                        self.profile_selected = item
                    elif self.play_mode:
                        pass
                    else:
                        self.item_selected = item
                    if self.options_mode:
                        op = self.options[self.option_selected]
                        if op == "Volume":
                            vol = self.options_dict["volume"]
                            if event.key == pygame.K_LEFT or joystick.JustWentLeft():
                                vol -= .1
                            if event.key == pygame.K_RIGHT or joystick.JustWentRight():
                                vol += .1
                            if vol < 0:
                                vol = 0
                            if vol > 1:
                                vol = 1
                            self.options_dict["volume"] = vol
                        if op == "Cache Screenshots":
                            if event.key == pygame.K_RETURN or joystick.JustPressedA():
                                self.options_dict["cache_screen_shots"] = not self.options_dict["cache_screen_shots"]
                        if op == "Stretch to Fullscreen":
                            if event.key == pygame.K_RETURN or joystick.JustPressedA():
                                self.options_dict["fullscreen"] = not self.options_dict["fullscreen"]
                        if op == self.DEL:
                            if event.key == pygame.K_RETURN or joystick.JustPressedA():
                                try:
                                    DID_SOMETHING = False
                                    for e, x in enumerate(os.listdir(fix_path(get_file("data/screenshots")))):
                                        os.remove(fix_path(get_file("data/screenshots/")) + x)
                                        DID_SOMETHING = True
                                    if DID_SOMETHING:
                                        print(colorize(f"Deleted screenshots: {e+1}", "green"))
                                        self.options[self.options.index(self.DEL)] = "Deleted screenshots"
                                        self.DEL = "Deleted screenshots"
                                except FileNotFoundError:
                                    print(colorize("Failed to delete screenshots!", "fail"))
                                    print(colorize("File not found error.", "fail"))
                    if event.key == pygame.K_x or joystick.JustPressedX():
                        if self.play_mode:
                            if self.profile_selected < 5 and not self.profiles[self.profile_selected].startswith("New"):
                                self.confirm_delete()
                    if event.key == pygame.K_RETURN or joystick.JustPressedA() or joystick.JustPressedStart():
                        if self.options_mode:
                            sel = self.option_selected
                            if self.options[sel] == "Cancel":
                                self.options_mode = False
                                self.options_dict = saves.load_options()
                            if self.options[sel] == "Save":
                                self.options_mode = False
                                saves.save_data("options", self.options_dict)
                            if not self.options_mode and self.options_lock:
                                self.done = True
                        elif self.play_mode:
                            if self.profiles[self.profile_selected] == "Back":
                                self.play_mode = False
                            else:
                                profile = saves.load_profile(self.profile_selected)
                                if profile["version"] != __version__:
                                    if profile["new"]:
                                        profile["version"] = __version__
                                    else:
                                        print(colorize("Warning!!! This profile is from a different version \
of Interplanetary Invaders!!!\nErrors may occur!!!", "warning"))
                                profile["new"] = False
                                saves.save_data(self.profile_selected, profile)
                                self.done = True
                        else:
                            sel = self.item_selected
                            if self.items[sel] == "Play":
                                self.play_mode = True
                            if self.items[sel] == "Options":
                                self.options_mode = True
                            if self.items[sel] == "Quit":
                                self.exit()
                            if self.items[sel] == "Credits":
                                run_credits(self.display, self.images)
                                pygame.mixer.music.load(fix_path(get_file("audio/music/MainMenu.mp3")))
                                pygame.mixer.music.play(-1)


    def exit(self):
        pygame.quit()
        sys.exit()

    def draw(self):
        if self.options_mode:
            self.draw_options()
        elif self.play_mode:
            self.draw_play()
        else:
            self.draw_menu()

    def draw_play(self):
        self.display.fill(0)
        self.draw_stars()
        stuff_rect = pygame.Rect((0, 0), (self.display.get_size()))
        stuff_rect.w *= .5
        stuff_rect.h *= .7
        stuff_rect.center = self.display.get_rect().center
        self.draw_menu_box(stuff_rect)
        self.draw_items(self.profiles, self.profile_selected, stuff_rect, x_off = 30)
        retro_text(stuff_rect.move(0, -50).midbottom, self.display, 15, "Press <x> to erase", anchor="center")

    def confirm_delete(self):
        stuff_rect = pygame.Rect(0, 0, 300, 400)
        stuff_rect.center = self.display.get_rect().center
        options = ["No", "Yes"]
        sel = 0
        done = False
        while not done:
            for event in pygame.event.get():
                joystick.Update(event)
                if event.type == pygame.KEYDOWN or joystick.WasEvent():
                    if not hasattr(event, "key"):
                        event.key = None
                    if event.key in (pygame.K_UP, pygame.K_w) or joystick.JustWentUp():
                        sel = 0
                    if event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_x) or joystick.JustWentDown():
                        sel = 1
                    if event.key == pygame.K_TAB:
                        sel = not sel
                    if event.key == pygame.K_RETURN or joystick.JustPressedA():
                        if sel:
                            os.remove(fix_path(get_file(f"data/profile{self.profile_selected}")))
                            self.profiles[self.profile_selected] = f"New Profile #{self.profile_selected + 1}"
                        self.pause_motion = True
                        done = True
            if not self.options_lock:
                self.draw_stars()
            self.draw_menu_box(stuff_rect)
            self.draw_items(options, sel, stuff_rect)
            retro_text(stuff_rect.move(0, 5).midtop, self.display, 14, "Are you sure you want", anchor="midtop")
            retro_text(stuff_rect.move(0, 20).midtop, self.display, 14, f"to erase Profile #{self.profile_selected + 1}?", anchor="midtop")
            pygame.display.update()

    def draw_stars(self):
        star_surf = pygame.transform.rotate(pygame.transform.scale(stars.main(), stars.REG_SIZE), self.star_rotation)
        star_rect = star_surf.get_rect()
        star_rect.center = (400, 300)
        self.display.blit(star_surf, star_rect)

    def draw_options(self):
        if not self.options_lock:
            self.display.fill(0)
            self.draw_stars()
        else:
            self.display.blit(self.background, (0, 0))
        stuff_rect = pygame.Rect((0, 0), (self.display.get_size()))
        stuff_rect.w *= .8
        stuff_rect.h *= .8
        stuff_rect.center = self.display.get_rect().center
        self.draw_menu_box(stuff_rect)
        self.draw_items(self.options, self.option_selected, stuff_rect)
        build_bar(self.display, (stuff_rect.left + 300, stuff_rect.top + 50), self.options_dict["volume"], startmark = "Low", endmark = "Hi")
        self.display.blit(self.bool_images[self.options_dict["cache_screen_shots"]], (stuff_rect.left + 470, stuff_rect.top + 93))
        self.display.blit(self.bool_images[self.options_dict["fullscreen"]], (stuff_rect.left + 545, stuff_rect.top + 173))

    def draw_menu_box(self, stuff_rect):
        stuff_surf = pygame.Surface(stuff_rect.size)
        stuff_surf.fill(0)
        stuff_surf.set_alpha(150)
        pygame.draw.line(self.display, (60, 60, 5), stuff_rect.topleft, stuff_rect.bottomleft)
        pygame.draw.line(self.display, (60, 60, 5), stuff_rect.topleft, stuff_rect.topright)
        pygame.draw.line(self.display, (60, 60, 5), stuff_rect.topright, stuff_rect.bottomright)
        pygame.draw.line(self.display, (60, 60, 5), stuff_rect.bottomleft, stuff_rect.bottomright)
        self.display.blit(stuff_surf, stuff_rect)

    def draw_menu(self):
        self.display.fill(0)
        self.draw_stars()
        logo = pygame.transform.scale(self.images[f"logo{str(self.frame).zfill(4)}"], LOGO_SIZE)
        lrect = logo.get_rect()
        lrect.midtop = (400, 0)
        self.display.blit(logo, lrect)
        stuff_rect = pygame.Rect((0, 0), (400, 550 - LOGO_SIZE[1]))
        stuff_rect.midtop = (400, LOGO_SIZE[1])
        if self.finished:
            self.draw_menu_box(stuff_rect)
            self.draw_items(self.items, self.item_selected, stuff_rect)
            retro_text(stuff_rect.bottomright, self.display, 14, f"V{__version__}", anchor="bottomright")

    def draw_items(self, items, selected, stuff_rect, x_off = 100):
        for n, x in enumerate(items):
            color = (255, 255, 255)
            if n == selected:
                self.display.blit(self.images["bullet"], (stuff_rect.left + x_off, stuff_rect.top + 50 + n * 40))
                color = (255, 255, 175)
            retro_text((stuff_rect.left + x_off, stuff_rect.top + 50 + n * 40), self.display, 20, " " + x, color = color)

    def update(self):
        self.text_time += self.time_passed
        if self.text_time >= self.text_rate and self.text and not self.options_lock:
            print(self.text[0], end = "", flush = True)
            self.text = self.text[1:]
            if not self.text:
                print()
            self.text_time = 0
        if self.frame_time >= self.frame_rate and not self.finished:
            self.frame += 1
            self.frame_time = 0
        if self.frame > 150:
            self.frame = 150
            self.finished = True
        if self.finished and self.frame != 150:
            self.frame = 150
        self.frame_time += self.time_passed
        self.star_rotation += self.rotation_speed * self.time_passed
        pygame.display.update()
        time_passed = clock.tick(60) / 1000
        if not self.pause_motion:
            self.time_passed = time_passed
        else:
            self.pause_motion = False
