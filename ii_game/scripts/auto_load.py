"""Autoloader gets images from IMAGE_PATH and puts in in a dictionary"""

import sys
import os
import time
import pygame

from ii_game.scripts.get_file import get_file
from ii_game.scripts.utils import colorize, fix_path
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts import joystick
from ii_game import __version__

IMAGE_PATH = get_file(fix_path("images/bitmap/"))

BAR_WIDTH = 200
BAR_HEIGHT = 30

def remove_extension(filename):
    """Remove the extension from a filename string"""
    return filename[:filename.index(".")]

def fetch_images(display):
    """Collect images from the IMAGE_PATH and return dictionary
with pygame.Surface objects as values and their names as keys"""
    names = []
    images = []
    num = 0
    print("Loading... \n")
    mx = 0
    display.fill((0, 0, 0))
    retro_text(display.get_rect().move(0, -30).center, display, 18, "LOADING...", anchor="center")
    retro_text(display.get_rect().move(0, 50).midtop, display, 22, "INTERPLANETARY INVADERS", anchor="center", bold=True)
    retro_text(display.get_rect().move(0, 75).midtop, display, 18, f"V{__version__}", anchor="center", bold=True)
    if joystick.hasJoystick:
        retro_text(display.get_rect().move(0, 200).center, display, 18, "Detected Joystick:", anchor="center", bold=True)
        retro_text(display.get_rect().move(0, 225).center, display, 20, '"' + joystick.name + '"', anchor="center", bold=True)
        if not joystick.IsSupported():
            retro_text(display.get_rect().move(0, 240).center, display, 20, "Unsupported Joystick", anchor="center", bold=True, color=(255, 0, 0))
    borderRect = pygame.Rect(0, 0, BAR_WIDTH + 10, BAR_HEIGHT + 5)
    borderRect.center = display.get_rect().center
    barRect = borderRect.copy()
    barRect.h = BAR_HEIGHT
    barRect.center = borderRect.center
    LastRefresh = 0
    pygame.display.update()
    for data in os.walk(IMAGE_PATH):
        for collect_file in data[2]:
            if not collect_file.startswith("."):
                mx += 1
    for data in os.walk(IMAGE_PATH):
        root = data[0]
        files = data[2]
        for collect_file in files:
            if not collect_file.startswith("."):
                num += 1
                name = remove_extension(collect_file)
                names.append(name)
                img = pygame.image.load(root + os.sep + collect_file)
                if (name.startswith("spinning") and not "RGBA" in name):
                    img = img.convert()
                    img.set_colorkey((0, 0, 0))
                else:
                    if not "animation" in root:
                        if name.startswith("map_"):
                            img = img.convert()
                        else:
                            img = img.convert_alpha()
                images.append(img)
                print(f"\rLoaded {colorize(num, 'blue' if num!=mx else 'green')} / {colorize(mx, 'green')} images   %s" % colorize(collect_file + (" " * (40 - len(collect_file))), 'bold'), flush = True, end = "")
            if time.time() - LastRefresh >= .15:
                LastRefresh = time.time()
                barRect.w = BAR_WIDTH * (num / mx)
                pygame.draw.rect(display, (0, 255, 0), barRect)
                for x in range(0, BAR_WIDTH, 20):
                    X_Val = barRect.x + x
                    pygame.draw.line(display, (0, 0, 0), (X_Val, borderRect.y), (X_Val, borderRect.y + borderRect.h), 2)
                pygame.draw.rect(display, (25, 25, 25), borderRect, 1)
                text, text_rect = retro_text(display.get_rect().move(0, 30).center, display, 18, f"{round(num/mx*100)}%", anchor="center", eraseColor=(0, 0, 0))
                pygame.display.update([barRect, text_rect])
    print()
    return dict(zip(names, images)), num
