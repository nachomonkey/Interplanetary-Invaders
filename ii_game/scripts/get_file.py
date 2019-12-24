from pkg_resources import resource_filename
from ii_game.scripts.utils import fix_path
import os
import pathlib

DEV_RUN = os.path.abspath(".").endswith("interplanetary-invaders")

def get_file(filename):
    if filename.startswith("data"):
        HOME = str(pathlib.Path().home())
        DIR = fix_path(f"{HOME}/.ii_game-data/") # Finds home directory
        if filename in ("data", fix_path("data/")):
            filename = ""
        else:
            filename = filename.replace(fix_path("data/"), "")
        if not os.path.exists(DIR):
            print(f"Building personal data directory:\n{DIR}")
            os.mkdir(DIR)
        return DIR+filename
    else:
        if DEV_RUN:   # Your running this as a devolper
            return fix_path("ii_game/") + filename # Find it in the current directory
        return resource_filename("ii_game", filename) # Find it in the installation
