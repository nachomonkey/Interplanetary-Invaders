import pygame
from pygame.math import Vector2 as V2
import math
import random

pygame.init()

STAR_SIZE = (5, 10)
CENTER_RADIUS = (30, 75)

SIZE = (1000, 1000)

REG_SIZE = SIZE

stars = []

class Star:
    def __init__(self):
        self.heading = math.radians(random.uniform(0, 359))
        self.velocity = V2([math.cos(self.heading), math.sin(self.heading)]) * random.uniform(.5, 1)
        self.size = random.randint(STAR_SIZE[0], STAR_SIZE[1])
        self.center = V2([SIZE[0] / 2, SIZE[1] / 2])
        self.center += V2(math.cos(self.heading), math.sin(self.heading)) * random.uniform(*CENTER_RADIUS)
        ColorType = random.choice([0] * 2 + [1] * 100 + [2] * 200)
        if ColorType == 0:
            self.color = (random.randint(175, 255), random.randint(0, 100), 0)
        if ColorType == 1:
            self.color = (random.randint(0, 50), random.randint(130, 255), random.randint(175, 255))
        if ColorType == 2:
            self.color = (220, random.randint(210, 255), random.randint(210, 255))

    def get_center(self):
        return (round(self.center[0]), round(self.center[1]))

    def dist_from_center(self):
        return math.hypot(self.center[0] - (SIZE[0] / 2), self.center[1] - (SIZE[1] / 2))

def main():
    surf = pygame.Surface(SIZE)
    surf.fill(0)
    scale = SIZE[0] / REG_SIZE[0]
    while len(stars) < 400:
        stars.append(Star())
    for star in stars:
        star.center += star.velocity + ((star.velocity / 5) * ((star.dist_from_center() ** 2 + 1) / 500))
        size = star.size * star.dist_from_center() / 500
        rect = pygame.Rect(0, 0, 10, 10)
        rect.center = star.center
        if not surf.get_rect().colliderect(rect):
            stars.remove(star)
            continue
        r = pygame.draw.circle(surf, star.color, star.get_center(), round(size * scale))
    return surf
