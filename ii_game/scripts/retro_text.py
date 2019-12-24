import pygame, os

pygame.init()

from ii_game.scripts.utils import fix_path
from ii_game.scripts.get_file import get_file

def retro_text(pos, display, size, text, font = "monospace", color = (255, 255, 255),  italic = False, bold = False, AA = False, underline = False, anchor = "topleft", render = True, res = 13, smooth = False, eraseColor = None):
    font = font.lower()
    if os.path.exists(get_file(fix_path("fonts/" + font + ".ttf"))):
        rfont = pygame.font.Font(get_file(fix_path(f"fonts/{font}.ttf")), res)
    else:
        rfont = pygame.font.SysFont(font, res)
    rfont.set_italic(italic)
    rfont.set_bold(bold)
    rfont.set_underline(underline)
    Text = rfont.render(str(text), AA, color)
    scale = pygame.transform.scale
    if smooth:
        scale = pygame.transform.smoothscale
    Text = pygame.transform.scale(Text, (int(Text.get_width() * (size / 8)), size))
    TextRect = Text.get_rect()
    setattr(TextRect, anchor, pos)
    if render:
        if eraseColor:
            pygame.draw.rect(display, eraseColor, TextRect)
        display.blit(Text, TextRect)
    return Text, TextRect
