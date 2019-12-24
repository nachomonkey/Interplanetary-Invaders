import pygame
import sys

pygame.init()

from ii_game.scripts.retro_text import retro_text
from ii_game.scripts.utils import fix_path
from ii_game.scripts.get_file import get_file
from ii_game.scripts import joystick

credits_text = """
Interplanetary Invaders

Developed & Created by:

NachoMonkey

Sound FX: NachoMonkey

Flak Sound [MODIFIED]:
zimbot (see README.md)

Animations, 3d images: NachoMonkey

Photo Credits

The following images are
in images/bitmap/map_images:

map_Jupiter.png: NASA
map_Mars.png: NASA
map_Mercury.png: NASA
map_Moon.png: NASA
map_Neptune.png: NASA
map_Saturn.png: NASA
map_Uranus.png: NASA
map_Venus.png: NASA

The following images are
in images/bitmap/backdrops

mars_backdrop[1-3].png: NASA
mars_cleanzone.png: NASA
mars_encampment[1-2].png: NASA
mars_volcano_backdrop.png [MODIFIED]: NASA
venus_backdrop[1-2].png: NASA
venus_backdrop_maatmons.png: NASA
venus_backdrop[4-5].png: NASA

images/bitmaps/(un)lock_exoplanets: NASA"""


def run_credits(display, images):
#    pygame.mixer.music.stop()
    pygame.mixer.music.load(get_file(fix_path("audio/music/stores.mp3")))
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    done = False
    text = []
    time_passed = 0
    for e, x in enumerate(credits_text.split("\n")):
        text.append(list(retro_text((400, 24 * e + 10), display, 14, x, font = "sans", anchor = "midtop", res = 11)))
    scroll = -600
    scroll_rate = 35
    while not done:
        for event in pygame.event.get():
            joystick.Update(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    done = True
            if joystick.BackEvent() or joystick.JustPressedA():
                done = True
        if scroll > 1000:
            done = True
        display.blit(images["background"], (0, 0))
        for line in text:
            if line[1][1] - scroll < 100:
                if line[0].get_width() <= 3:
                    text.remove(line)
                    continue
                s1 = line[0].get_width()
                if line[1][1] - scroll > 90:
                    s1 *= 1.025
                else:
                    s1 /= 1.03
                line[0] = pygame.transform.scale(line[0], (round(s1), line[0].get_height()))
                r2 = pygame.Rect((0, 0), line[0].get_size())
                r2.center = line[1].center
                line[1] = r2
            display.blit(line[0], (line[1][0], line[1][1] - scroll))
        scroll += scroll_rate * time_passed
        pygame.display.update()
        time_passed = clock.tick(60) / 1000
    pygame.mixer.music.stop()
