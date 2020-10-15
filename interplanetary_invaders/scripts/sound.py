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

def ChangeSoundPitch(filename, new_pitch=.5):
    fn = SOUND_PATH + os.path.split(filename)[-1]
    index = fn.rindex(".")
    fn, ext = fn[:index], fn[index+1:]
    fn += "_" + str(new_pitch) + ext
    if not os.path.exists(fn):
        with wave.open(filename, "r") as r:
            with wave.open(fn, "w") as w:
                w.setnchannels(r.getnchannels())
                w.setsampwidth(r.getsampwidth())
                w.setframerate(r.getframerate() * new_pitch)
                w.writeframes(r.readframes(r.getnframes()))
    return fn

class Sound(pygame.mixer.Sound):
    def __init__(self, filename, no_slow=False, pitch=1):
        self.original_filename = filename
        filename = get_file(filename)
        pitch = pitch
        global is_slow
        if not no_slow and is_slow:
            pitch /= 2
        if not pitch in (0, 1):
            filename = ChangeSoundPitch(filename, pitch)
        super().__init__(filename)
        self.set_volume(options["volume"])

    def set_volume(self, vol):
        super().set_volume(vol * options["volume"])
