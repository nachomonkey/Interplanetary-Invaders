import pygame

pygame.init()

def transition(Display, speed = 1):
    pygame.event.set_blocked(True)
    CLOCK = pygame.time.Clock()
    display = Display.copy()
    for alpha in range(0, 256, speed):
        Display.blit(display, (0, 0))
        surf = pygame.Surface(Display.get_size())
        surf.set_alpha(alpha)
        Display.blit(surf, (0, 0))
        pygame.display.update()
        CLOCK.tick(256)
    pygame.event.set_blocked(False)
