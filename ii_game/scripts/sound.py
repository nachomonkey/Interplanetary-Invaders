import pygame

pygame.init()

from ii_game.scripts import saves
from ii_game.scripts.get_file import get_file

shared = {"options" : saves.load_options()}

class Sound(pygame.mixer.Sound):
    def __init__(self, filename):
        filename = get_file(filename)
        super().__init__(filename)
        self.set_volume(shared["options"]["volume"])

    def set_volume(self, vol):
        super().set_volume(vol * shared["options"]["volume"])
