import pygame, os

pygame.init()

from interplanetary_invaders.scripts.utils import fix_path
from interplanetary_invaders.scripts.get_file import get_file

MAX_FONTS = 30

FONT_CACHE = {}

def font_checksum(size, font, italic, bold, underline):
    return str(size) + font + str(italic) + str(bold) + str(underline)

def retro_text(pos, surface, size, text, font="monospace", color=(255, 255, 255),  italic=False, bold=False, AA=False, underline=False, anchor="topleft", render=True, res=13, smooth=False, eraseColor=None):
    if len(FONT_CACHE) > MAX_FONTS:
        FONT_CACHE.clear()
    font = font.lower()
    checksum = font_checksum(size, font, italic, bold, underline)
    if checksum in FONT_CACHE:
        rfont = FONT_CACHE[checksum]
    else:
        if os.path.exists(get_file(fix_path("fonts/" + font + ".ttf"))):
            rfont = pygame.font.Font(get_file(fix_path(f"fonts/{font}.ttf")), res)
        else:
            rfont = pygame.font.SysFont(font, res)
        rfont.set_italic(italic)
        rfont.set_bold(bold)
        rfont.set_underline(underline)
        FONT_CACHE[checksum] = rfont
    Text = rfont.render(str(text), AA, color)
    scale = pygame.transform.scale
    if smooth:
        scale = pygame.transform.smoothscale
    Text = pygame.transform.scale(Text, (int(Text.get_width() * (size / 8)), size))
    TextRect = Text.get_rect()
    setattr(TextRect, anchor, pos)
    if render:
        if eraseColor:
            pygame.draw.rect(surface, eraseColor, TextRect)
        surface.blit(Text, TextRect)
    return Text, TextRect
