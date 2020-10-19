import os
import pathlib
from pkg_resources import resource_filename
from interplanetary_invaders.scripts.utils import fix_path

SOUND_PATH = fix_path("data/sound-cache/")
DEV_RUN = os.path.abspath(".").endswith("interplanetary-invaders")

def get_file(filename):
    if filename.startswith("data"):
        HOME = str(pathlib.Path().home())
        DIR = fix_path(f"{HOME}/.interplanetary_invaders-data/") # Finds home directory
        if filename in ("data", fix_path("data/")):
            filename = ""
        else:
            filename = filename.replace(fix_path("data/"), "")
        if not os.path.exists(DIR):
            print(f"Building personal data directory:\n{DIR}")
            os.mkdir(DIR)
        return DIR+filename
    else:
        if DEV_RUN:   # You're running this as a devolper
            return fix_path("interplanetary_invaders/") + filename # Find it in the current directory
        return resource_filename("interplanetary_invaders", filename) # Find it in the installation
