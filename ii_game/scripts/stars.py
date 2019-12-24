import pygame
import math
import random

pygame.init()

STAR_SIZE = (5, 10)

SIZE = (1000, 1000)

REG_SIZE = SIZE

stars = []

class Star:
    def __init__(self):
        self.heading = random.randint(0, 359)
        self.velocity = pygame.math.Vector2([math.cos(self.heading), math.sin(self.heading)]) * random.uniform(.5, 1)
        self.size = random.randint(STAR_SIZE[0], STAR_SIZE[1])
        self.center = pygame.math.Vector2([SIZE[0] / 2, SIZE[1] / 2])
        ColorType = random.choice([0] * 1 + [1] * 100 + [2] * 200)
        if ColorType == 0:
            self.color = (255, random.randint(0, 100), 0)
        if ColorType == 1:
            self.color = (0, random.randint(150, 255), random.randint(200, 255))
        if ColorType == 2:
            self.color = (220, random.randint(220, 255), random.randint(220, 255))

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
        star.center += star.velocity * ((star.dist_from_center() + 1) / 25)
        size = star.size * star.dist_from_center() / 500
        rect = pygame.Rect(0, 0, size * scale, size * scale)
        rect.center = star.center
        if not surf.get_rect().colliderect(rect):
            stars.remove(star)
            continue
        pygame.draw.circle(surf, star.color, star.get_center(), round(size * scale))
    return surf
