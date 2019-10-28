#!/usr/bin/env python3.7

import sys

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

from ii_game.scripts import menu
import pygame
from ii_game.scripts import auto_load
from ii_game.scripts import missions
from ii_game.scripts import saves
from ii_game.scripts.saves import load_options
saves.debugMode = debugMode
from ii_game.scripts import map_menus as maps
from ii_game.scripts import lose_win
from ii_game.scripts.congrats import congrats
from ii_game.scripts.planets import *
from ii_game.scripts import stores
from ii_game.scripts.achievements import ACHIEVEMENTS
from ii_game.scripts.get_file import get_file
from ii_game.scripts.utils import colorize
import os
import time

print(colorize(f"Your \"data\" directory is: {get_file('data')}", "bold"))

pygame.init()

SIZE = (800, 600)
from ii_game.scripts import game

class Main:
    def __init__(self):
        self.options = saves.load_options()
        fullscreen = 0
        if self.options["fullscreen"]:
            fullscreen = pygame.FULLSCREEN
        self.Display = pygame.display.set_mode((800, 600), fullscreen | pygame.HWSURFACE | pygame.HWACCEL | pygame.DOUBLEBUF)
        self.display = pygame.Surface((800, 600))
        pygame.display.set_caption("Interplanetary Invaders")
        pygame.display.set_icon(pygame.image.load(get_file("icon.png")))
        t1 = time.time()
        self.images, num = auto_load.fetch_images(self.Display)
        t2 = time.time()
        print(colorize(f"Loaded {num} images in {round(t2-t1, 2)} seconds", "green"))
        self.menu()
        self.cat = []

    def menu(self):
        self.Menu = menu.Menu(self.Display, self.images)
        self.Menu.text = ""
        self.Menu.main()
        self.profile_selected = self.Menu.profile_selected
        self.profile = saves.load_profile(self.profile_selected)
        self.planets = [Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, Neptune]

    def keepGoing(self, lw):
        try:
            lw.main()
        except KeyboardInterrupt:
            print(colorize("Nope. Answer the questions", "fail"))
            self.keepGoing(lw)

    def main(self):
        point = None
        while True:
            Map = maps.Map(self.images, self.Display, self.profile, self.profile_selected, point)
            mission, point = Map.main()
            old_mission = mission
            if Map.toMenu:
                self.menu()
                point = None
                continue
            play = game.Game(self.display, self.Display, self.images, mission, self.profile, self.profile_selected)
            score, mode, acc, maxcombo = play.main()
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
            if mode == "won":
                play.victory()
                self.profile["addNewStore"] -= 1
                self.profile["money"] += round(mission().bonus * self.acc_per)
                self.profile["money"] += round(mission().bonus / (p.lost + 1))
                ach = []
                if acc.count(True) == len(acc) and acc:
                    ach.append("archer")
                if maxcombo > 4:
                    ach.append("combo5")
                if maxcombo > 9:
                    ach.append("combo10")
                if maxcombo > 14:
                    ach.append("combo15")
                if maxcombo > 19:
                    ach.append("combo20")
                for a in ach:
                    if ACHIEVEMENTS[a][0] in self.profile["achievements"]:
                        continue
                    congrats(self.Display, self.images, "ach", ACHIEVEMENTS[a], self.profile)
            self.profile = play.profile
            for p in self.profile["map"][self.profile["planet"].name]:
                if not hasattr(p, "bonus"):
                    p.bonus = False
                if p.alien_flag and not p.bonus:
                    not_finished = True
            if not not_finished and not self.profile["planet"].name in self.profile["finished_planets"]:
                for name in self.profile["planet"].unlocks:
                    for p in self.planets:
                        if p.name == name:
                            congrats(self.Display, self.images, "planet", p)
                play.profile["finished_planets"].append(self.profile["planet"].name)
                self.profile["finished_planets"].append(self.profile["planet"].name)
            r = False
            while not r:
                r = stores.confirmStores(self.profile, self.Display, self.images)
            self.profile = r
            saves.save_data(self.profile_selected, self.profile)
            del play
            if lw.exit:
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
