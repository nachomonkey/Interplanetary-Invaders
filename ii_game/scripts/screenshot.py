import os
import pygame
import time
import copy
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts.sound import Sound
from ii_game.scripts.utils import fix_path, colorize
from ii_game.scripts.get_file import get_file

from ii_game.scripts import saves
directory = get_file(fix_path("data/screenshots"))

pygame.init()

sound = Sound(fix_path("audio/click.wav"))
options = saves.load_options()
save_for_later = {}

FirstScreenshot = True

def capture(profile_num, surf, ingame = False):
    global FirstScreenshot
    if FirstScreenshot:
        print(colorize(f"Saving screenshots at: {directory}", "bold"))
        FirstScreenshot = False
    surf = copy.copy(surf)
    data = time.localtime()
    if not os.path.exists(directory):
        print(colorize("Screenshot directory missing.", "warning"))
        os.mkdir(directory)
    name = f"ii{profile_num}_{data.tm_year}{data.tm_mon}{data.tm_mday}{data.tm_hour}{data.tm_min}{data.tm_sec}"
    done_this = False
    p = fix_path(directory+"/"+name+".png")
    while os.path.exists(p) or name in save_for_later:
        if not done_this:
            name += "_2"
            done_this = True
        else:
            name = name[:-1] + str(int(name[-1]) + 1)
        p = fix_path(directory+"/"+name+".png")
    sound.play()
    if ingame and options["cache_screen_shots"]:
        print(colorize(f"Caching screenshot {name}", "blue"))
        save_for_later[name] = surf
    else:
        save(surf, name)

def save(surf, name):
    print(colorize("Saving screenshot...", "blue"))
    t1 = time.time()
    pygame.image.save(surf, fix_path(f"{directory}/{name}.png"))
    t2 = time.time()
    print(colorize(f"Saved screenshot \"{name}\" in {round(t2-t1, 2)} seconds", "green"))

def update(surf):
    if save_for_later:
        retro_text((400, 200), surf, 20, "Saving your cached screenshots", anchor = "center")
        retro_text((400, 220), surf, 15, "To disable this feature go to the options menu", anchor = "center")
        pygame.display.update()
    for x in save_for_later:
        save(save_for_later[x], x)
    save_for_later.clear()
