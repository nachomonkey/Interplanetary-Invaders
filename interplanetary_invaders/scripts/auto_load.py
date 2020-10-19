"""Autoloader gets images from IMAGE_PATH and puts in in a dictionary"""

import sys
import os
import time
import pygame

from interplanetary_invaders.scripts.get_file import get_file
from interplanetary_invaders.scripts.sprites import extract_sprites
from interplanetary_invaders.scripts.utils import colorize, fix_path, lerp, remove_extension
from interplanetary_invaders.scripts.retro_text import retro_text
from interplanetary_invaders.scripts import joystick
from interplanetary_invaders import __version__

IMAGE_PATH = get_file(fix_path("images/bitmap/"))

BAR_WIDTH = 200
BAR_HEIGHT = 30

HUE_BLUE = 240
HUE_CYAN = 180

def fetch_images(display):
    """Collect images from the IMAGE_PATH and return dictionary
with pygame.Surface objects as values and their names as keys"""
    names = []
    images = []
    num = 0
    mx = 0
    display.fill((0, 0, 0))
    retro_text(display.get_rect().move(0, -30).center, display, 18, "LOADING...", anchor="center")
    for x in range(10):
        g = 255 * x / 10
        retro_text(display.get_rect().move(0, 60 - x).midtop, display, 22, "INTERPLANETARY INVADERS", anchor="center", bold=True, color=(0, g, 0))
        retro_text(display.get_rect().move(0, 85 - x).midtop, display, 18, f"V{__version__}", anchor="center", bold=True, color=(0, g * .75, 0))
    if joystick.hasJoystick:
        retro_text(display.get_rect().move(0, 200).center, display, 18, "Detected Joystick:", anchor="center", bold=True)
        retro_text(display.get_rect().move(0, 225).center, display, 20, '"' + joystick.name + '"', anchor="center")
        if not joystick.IsSupported():
            retro_text(display.get_rect().move(0, 240).center, display, 20, "Unsupported Joystick", anchor="center", bold=True, color=(255, 0, 0))
    borderRect = pygame.Rect(0, 0, BAR_WIDTH + 10, BAR_HEIGHT + 5)
    borderRect.center = display.get_rect().center
    pygame.draw.rect(display, (100, 100, 100), borderRect, 1)
    barRect = borderRect.copy()
    barRect.h = BAR_HEIGHT
    barRect.center = borderRect.center
    barRect.x += 2
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
                img = pygame.image.load(root + os.sep + collect_file)
                store_img = True
                print(f"\rLoading image {colorize(num, 'blue' if num!=mx else 'green')} of {colorize(mx, 'green')}  %s" % colorize(collect_file + (" " * (40 - len(collect_file))), 'bold'), flush=True, end="")
                if name.startswith("NoA_"):
                    name = name.split("NoA_")[1]
                    img = img.convert()
                elif (name.startswith("spinning") and not "RGBA" in name):
                    img = img.convert()
                    img.set_colorkey((0, 0, 0))
                else:
                    if not "animation" in root:
                        if name.startswith("map_"):
                            img = img.convert()
                        else:
                            img = img.convert_alpha()
                if name.startswith("ROT_"):
                    name = name[4:]
                    x = 0
                    for r in range(-90, 91):
                        x += 1
                        names.append(name + str(int(r % 360)))
                        images.append(pygame.transform.rotate(img, r))
                if name.endswith("_sheet"):
                    name = name.split("_sheet")[0]
                    for e, surf in enumerate(extract_sprites(img)):
                        names.append(name + str(e + 1))
                        images.append(surf)
                    store_img = False
                if store_img:
                    names.append(name)
                    images.append(img)
            if time.time() - LastRefresh >= .025:
                LastRefresh = time.time()
                barRect.w = int((BAR_WIDTH * (num / mx)) * 10) / 10
                color = pygame.color.Color(0)
                hue = lerp(HUE_BLUE, HUE_CYAN, num / mx)
                color.hsva = (hue, 100, 100, 100)
                pygame.draw.rect(display, color, barRect)
                for x in range(0, BAR_WIDTH, BAR_WIDTH // 10)[1:]:
                    X_Val = barRect.x + x
                    pygame.draw.line(display, (0, 0, 0), (X_Val, borderRect.y), (X_Val, borderRect.y + borderRect.h), 1)
                text, text_rect = retro_text(display.get_rect().move(0, 30).center, display, 18, f"{round(num/mx*100)}%", anchor="center", eraseColor=(0, 0, 0))
                pygame.display.update([barRect, text_rect])

                # This makes pygame rerender the screen when the window is brought up
                for event in pygame.event.get():
                    pass
    print()
    return dict(zip(names, images)), num
