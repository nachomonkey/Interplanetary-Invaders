import pygame, time

pygame.init()

display = pygame.display.set_mode((100, 100))

COLOR1 = (255, 255, 0)
COLOR2 = (255, 0, 0)

STEPS = 100

for x in range(1, STEPS + 1):
    pygame.draw.circle(display, (255, round(255 * (STEPS - x) / STEPS), 0), (50, 50), (STEPS - x) // 2)

pygame.display.update()

time.sleep(3)
