import sys
import pygame

pygame.init()

from interplanetary_invaders.scripts.retro_text import retro_text
from interplanetary_invaders.scripts.utils import fix_path
from interplanetary_invaders.scripts.get_file import get_file
from interplanetary_invaders.scripts import joystick

credits_text = """
:-:INTERPLANETARY INVADERS:-:
-----------------------------
--CREATED & DEVELOPED BY--
NachoMonkey

--SOUND FX--
NachoMonkey

Flak Sound (modified):
zimbot

Cash Register:
kiddpark

Green Alien Crash (modified):
spoonsandlessspoons

--GRAPHICS & VFX--
NachoMonkey

--PHOTO CREDITS--
Credit to NASA for the maps for:
Jupiter, Mars, Mercury, the Moon,
Neptune, Saturn, Uranus, Venus

Credit to NASA for the following mission backdrop images:
mars_backdrop[1-3], mars_cleanzone, mars_encampment[1-2],
mars_volcano_backdrop (modified), venus_backdrop[1-2],
venus_backdrop_maatmons, venus_backdrop[4-5]

--Other contributers--
XracerX


-----------------------



This game was made using pygame
https://pygame.org











thanks for playing!
"""


def run_credits(display, images):
#    pygame.mixer.music.stop()
    pygame.mixer.music.load(get_file(fix_path("audio/music/Credits.ogg")))
    pygame.mixer.music.play(-1)
    clock = pygame.time.Clock()
    done = False
    text = []
    time_passed = 0
    for e, x in enumerate(credits_text.split("\n")):
        text.append(list(retro_text((400, 24 * e + 10), display, 14, x, font = "sans", anchor = "midtop", res = 11)))
    scroll = -600
    scroll_rate = 50
    total_length = 1400
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
        if scroll > total_length:
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
        img = images["nachomonkeylogo"]
        img_rect = img.get_rect()
        img_rect.centerx = display.get_width() // 2
        img_rect.top = total_length - img_rect.height - scroll - 175
        display.blit(img, img_rect)
        scroll += scroll_rate * time_passed
        pygame.display.update()
        time_passed = clock.tick(60) / 1000
    pygame.mixer.music.stop()
