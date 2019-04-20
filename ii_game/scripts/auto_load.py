"""Autoloader gets images from IMAGE_PATH and puts in in a dictionary"""

import sys
import os
import pygame

from ii_game.scripts.get_file import get_file
from ii_game.scripts.utils import colorize, fixPath

IMAGE_PATH = get_file(fixPath("images/bitmap/"))

def remove_extension(filename):
    """Remove the extension from a filename string"""
    return filename[:filename.index(".")]

def fetch_images():
    """Collect images from the IMAGE_PATH and return dictionary
with pygame.Surface objects as values and their names as keys"""
    names = []
    images = []
    num = 0
    print("Loading... \n")
    mx = 0
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
    print()
    return dict(zip(names, images)), num
