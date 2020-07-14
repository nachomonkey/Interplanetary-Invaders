import pygame
import random
import time

pygame.init()

HEIGHT = (75, 125)
X_RAND = (-.2, .6)

COLOR = (0, 255, 255)
GREEN = (45, 255, 18)

GREEN_ON = False

DAMAGE_PER_SEC = 1

MAX_THINGS = 5

def main(start, to):
    lines = []
    done = False
    while True:
        if len(lines) == 0:
            lines.append((start, next_point(start, to)[0]))
        else:
            np, done = next_point(lines[-1][1], to)
            lines.append((lines[-1][1], np))
            if done:
                return lines

def next_point(start, to):
    x_change = start[0] - to[0]
    x_change *= random.uniform(*X_RAND)
    y_change = random.uniform(*HEIGHT)
    done = False
    if start[1] - y_change < to[1]:
        x_change = start[0] - to[0]
        y_change = start[1] - to[1]
        done = True
    return (start[0] - x_change, start[1] - y_change), done

def run(start, aliens, GOs, player, display, time_passed):
    color = COLOR
    bonus = 1
    if GREEN_ON:
        bonus = 2
        color = GREEN
    lines = []
    things_hit = 0
    for g in GOs:
        if g.dead or g.type == "moneyBag" or g.type == "aircraft":
            continue
        rect = g.get_rect()
        rect.h = 1000
        pRect = player.get_rect()
        center = pRect.center
        pRect.w *= 2
        pRect.center = center
        if not rect.colliderect(pRect):
            continue
        if things_hit == MAX_THINGS:
            continue
        things_hit += 1
        lines += main(start, g.get_rect().center)
        g.health -= DAMAGE_PER_SEC * time_passed * bonus
        if g.health <= 0:
            g.dead = True
    while things_hit < MAX_THINGS:
        to_hit = 0
        for a in aliens:
            if a.dead == 1:
                continue
            if things_hit == MAX_THINGS:
                continue
            to_hit += 1
            things_hit += 1
            for x in range(random.randint(1, 2)):
                lines += main(start, a.get_rect().center)
                a.health -= DAMAGE_PER_SEC * time_passed * bonus
                if a.health < 0:
                    a.health = 0
                    a.hitBy = "lightning"
        if to_hit == 0:
            break
    for l in lines:
        pygame.draw.line(display, color, l[0], l[1], bonus)
