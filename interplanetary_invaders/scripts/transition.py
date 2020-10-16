import pygame

pygame.init()

Clock = pygame.time.Clock()

def black_out(display, speed=1):
    pygame.event.set_blocked(True)
    background = display.copy()
    for alpha in range(0, 256, speed):
        display.blit(background, (0, 0))
        surf = pygame.Surface(display.get_size())
        surf.set_alpha(alpha)
        display.blit(surf, (0, 0))
        pygame.display.update()
        Clock.tick(256)
    pygame.event.set_blocked(False)

def fade_in(display, speed=1, background=None):
    pygame.event.set_blocked(True)
    target_surf = display.copy()
    ratio = display.get_width() / display.get_height()
    y_range = list(range(0, target_surf.get_height(), speed))
    if y_range:
        if y_range[-1] != target_surf.get_height():
            y_range.append(target_surf.get_height())
    for e, y in enumerate(y_range):
        if y != target_surf.get_height():
            if y > 75 and e % 16:
                continue
            if y > 150 and e % 8:
                continue
            if y > 250 and e % 4:
                continue
            if y > 400 and e % 2:
                continue
        scale = (round(ratio * y), y)
        if not background:
            display.fill((0, 0, 0))
        else:
            display.blit(background, (0, 0))
        surf = pygame.transform.scale(target_surf, scale)
        surf = pygame.transform.scale(surf, display.get_size())
        surf.set_alpha(y / target_surf.get_height() * 255)
        display.blit(surf, (0, 0))
        pygame.display.update()
        Clock.tick(256)
    pygame.event.set_blocked(False)
