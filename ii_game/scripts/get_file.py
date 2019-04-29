from pkg_resources import resource_filename
from ii_game.scripts.utils import fixPath
import os

DEV_RUN = os.path.abspath(".").endswith("interplanetary-invaders")

def get_file(filename):
    if filename.startswith("data"):
        DIR = fixPath(f"{os.environ['HOME']}/.ii_game-data/")
        if filename in ("data", fixPath("data/")):
            filename = ""
        else:
            filename = filename.replace(fixPath("data/"), "")
        if not os.path.exists(DIR):
            print(f"Building personal data directory:\n{DIR}")
            os.mkdir(DIR)
        return DIR+filename
    else:
        if DEV_RUN:   # Your running this as a devolper
            return fixPath("ii_game/") + filename # Find it in the current directory
        return resource_filename("ii_game", filename) # Find it in the installation
