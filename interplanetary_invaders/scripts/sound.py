import os
import wave
import pygame

pygame.init()

from interplanetary_invaders import __version__ as ver
from interplanetary_invaders.scripts import saves
from interplanetary_invaders.scripts.get_file import get_file, SOUND_PATH
from interplanetary_invaders.scripts.utils import fix_path

options = saves.load_options()

is_slow = False

SOUND_PATH = get_file(SOUND_PATH)
if not os.path.exists(SOUND_PATH):
    os.mkdir(SOUND_PATH)

versionFile = SOUND_PATH + "version"

if os.path.exists(versionFile):
    with open(versionFile) as file:
        if file.read() != ver:
            for f in os.listdir(SOUND_PATH):
                if f != "version":
                    os.remove(SOUND_PATH + f)

with open(versionFile, "w") as file:
    file.write(ver)

def SlowDownSound(filename):
    fn = SOUND_PATH + filename.split("/")[-1]
    if not os.path.exists(fn):
        with wave.open(filename, "r") as r:
            with wave.open(fn, "w") as w:
                w.setnchannels(r.getnchannels())
                w.setsampwidth(r.getsampwidth())
                w.setframerate(r.getframerate() / 2)
                w.writeframes(r.readframes(r.getnframes()))
    return fn

class Sound(pygame.mixer.Sound):
    def __init__(self, filename, no_slow=False):
        self.original_filename = filename
        filename = get_file(filename)
        global is_slow
        if not no_slow and is_slow:
            filename = SlowDownSound(filename)
        super().__init__(filename)
        self.set_volume(options["volume"])

    def set_volume(self, vol):
        super().set_volume(vol * options["volume"])
