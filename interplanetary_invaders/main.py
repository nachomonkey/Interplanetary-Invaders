#!/usr/bin/env python3.7

import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import sys
import time

debugMode = False
if len(sys.argv) > 1 and __name__ == "__main__":
    if sys.argv[1] in ("help", "-h", "--help"):
        print("\nWelcome to Interplanetary Invaders\n")
        print("Usage: python3 main.py [OPTIONS]")
        print("\nOptions:\n")
        print("--help: Display this help message")
        print("--verbose: Show debug info")
        sys.exit()
    if sys.argv[1] in ("--verbose", "-v"):
        debugMode = True
        print("Verbose mode enabled")

from interplanetary_invaders.scripts import menu

import pygame

from interplanetary_invaders.scripts import auto_load
from interplanetary_invaders.scripts import missions
from interplanetary_invaders.scripts import saves
from interplanetary_invaders.scripts.saves import load_options
from interplanetary_invaders.scripts import map_menus as maps
from interplanetary_invaders.scripts import lose_win
from interplanetary_invaders.scripts.congrats import congrats
from interplanetary_invaders.scripts.planets import *
from interplanetary_invaders.scripts import stores
from interplanetary_invaders.scripts.achievements import ACHIEVEMENTS
from interplanetary_invaders.scripts.get_file import get_file
from interplanetary_invaders.scripts.utils import colorize, set_images
from interplanetary_invaders.scripts.transition import black_out
from interplanetary_invaders.scripts import joystick
from interplanetary_invaders.scripts import game

print(colorize(f"Your data directory is: {get_file('data')}", "bold"), "\n")

pygame.init()

saves.debugMode = debugMode

SIZE = (800, 600)

if joystick.hasJoystick:
    print(colorize(f"Detected a \"{joystick.name}\" Joystick", "green" if joystick.IsSupported() else "fail"))
    if not joystick.IsSupported():
        print(colorize(f"This joystick may not be supported", "warning"))

images = {}

class Main:
    def __init__(self):
        self.options = saves.load_options()
        fullscreen = 0
        if self.options["fullscreen"]:
            fullscreen = pygame.FULLSCREEN
        pygame.display.set_icon(pygame.image.load(get_file("icon.png")))
        self.Display = pygame.display.set_mode((800, 600), fullscreen | pygame.HWACCEL)
        self.display = pygame.Surface((800, 600))
        pygame.display.set_caption("Interplanetary Invaders")
        t1 = time.time()
        self.images, num = auto_load.fetch_images(self.Display)
        t2 = time.time()
        self.first_time = True
        print(colorize(f"Loaded {num} images in {round(t2-t1, 2)} seconds", "green"))

        set_images(self.images)

        self.menu()
        self.cat = []

    def menu(self):
        self.Menu = menu.Menu(self.Display, self.images)
        if self.first_time:
            self.first_time = False
        else:
            self.Menu.text = ""
        self.Menu.main()
        self.profile_selected = self.Menu.profile_selected
        self.profile = saves.load_profile(self.profile_selected)

    def keepGoing(self, lw):
        lw.main()
#        try:
#            lw.main()
#        except KeyboardInterrupt:
#            print(colorize("Nope. Answer the questions", "fail"))
#            self.keepGoing(lw)

    def main(self):
        point = None
        retry = False
        mission = None
        while True:
            if not retry:
                Map = maps.Map(self.images, self.Display, self.profile, self.profile_selected, point)
                mission, point = Map.main()
                old_mission = mission
                if Map.toMenu:
                    background = self.Display.copy()
                    self.menu()
                    point = None
                    continue
            play = game.Game(self.display, self.Display, self.images, mission, self.profile, self.profile_selected, retry)

            retry = False
            score, mode, acc, maxcombo, im_back = play.main()
            if play.toMenu:
                self.menu()
                point = None
                continue
            try:
                self.acc_per = acc.count(True) / len(acc)
            except ZeroDivisionError:
                self.acc_per = 0
            for p in self.profile["map"][self.profile["planet"].name]:
                if p.mission == mission:
                    if mode == "lost":
                        p.lost += 1
                    break
            lw = lose_win.LoseWin(self.Display, self.images, (self.profile["money"], self.profile["money"] + score, mission().bonus / (p.lost + 1), mission().bonus, acc, p.lost + 1, maxcombo), mode=mode)
            self.keepGoing(lw)
            not_finished = False
            ach = []
            if im_back:
                ach.append("im_back")  # I'm Back Achievement
            if mode == "won":
                play.victory()
                self.profile["addNewStore"] -= 1
                self.profile["money"] += round(mission().bonus * self.acc_per)
                self.profile["money"] += round(mission().bonus / (p.lost + 1))
                if acc.count(True) >= ((len(acc) / 4) * 3) and acc:
                    ach.append("archer")
                if maxcombo > 4:
                    ach.append("combo5")
                if maxcombo > 9:
                    ach.append("combo10")
                if maxcombo > 14:
                    ach.append("combo15")
                if maxcombo > 19:
                    ach.append("combo20")

                for name in mission().unlocks_planets:
                    for p in planetsmoons:
                        if p.name == name:
                            self.profile["unlocked_planets"].append(name)
                            congrats(self.Display, self.images, "planet", p)
            for a in ach:
                if ACHIEVEMENTS[a][0] in self.profile["achievements"]:
                    continue
                congrats(self.Display, self.images, "ach", ACHIEVEMENTS[a], self.profile)
            r = False
            while not r:
                r = stores.confirmStores(self.profile, self.Display, self.images)
            self.profile = r
            saves.save_data(self.profile_selected, self.profile)
            del play
            retry = lw.retry
            if lw.exit:
                black_out(self.Display, 2)
                pygame.quit()
                sys.exit()

class Display(pygame.Surface):
    def __init__(self, display, size):
        super().__init__(size)
        self.expand = False
        self.display = display

    def update(self):
        if self.expand:
            r = self.display.get_rect()
            r2 = pygame.Rect(0, 0, 800, 600)
            r2.center = r.center
            self.display.blit(self, r2)
        else:
            self.display.blit(self, (0, 0))

def run():
    try:
        main = Main()
        main.main()
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    run()
