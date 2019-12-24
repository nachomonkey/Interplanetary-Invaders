import pygame
import sys
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts.confirm import confirmExit
from ii_game.scripts import screenshot
from ii_game.scripts.sound import Sound
from ii_game.scripts.utils import fix_path
from ii_game.scripts import joystick

pygame.init()

clock = pygame.time.Clock()

class LoseWin:
    def __init__(self, display, images, money = [1, 1, 1, 1, [], 0, 0], mode = "won"):
        self.display = display
        self.images = images
        self.mode = mode
        self.frame = 1
        self.frame_time = 0
        self.frame_rate = 1 / 25
        self.time_passed = 0
        self.anim_done = False
        self.done = False
        self.text = ["Save + Continue", "Save + Exit"]
        self.top_selected = True
        self.money_old, self.money_new, self.bonus, self.bonus1, self.acc, self.lost, self.maxcombo = money
        try:
            self.acc_per = self.acc.count(True) / len(self.acc)
            self.acc_per2 = round(self.acc_per * 100, 3)
        except ZeroDivisionError:
            self.acc_per = 0
            self.acc_per2 = 0
        self.money_new += round(self.bonus)
        self.money_new += round(self.bonus1 * self.acc_per)
        self.money_sound = Sound(fix_path("audio/money.wav"))
        if mode == "won":
            self.money_sound.play(-1)
        self.exit = False

    def main(self):
        while not self.done:
            self.events()
            self.draw()
            self.update()
        return self.exit

    def events(self):
        for event in pygame.event.get():
            joystick.Update(event)
            if not hasattr(event, "key"):
                event.key = None
            if event.type == pygame.KEYUP or joystick.WasEvent():
                if event.key == pygame.K_F2 or joystick.JustPressedLB():
                    screenshot.capture("WL", self.display)
                if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                    self.money_old = self.money_new
                if event.key == pygame.K_TAB:
                    self.top_selected = not self.top_selected
                if event.key == pygame.K_UP or joystick.JustWentUp():
                    self.top_selected = True
                if event.key == pygame.K_DOWN or joystick.JustWentDown():
                    self.top_selected = False
                if event.key == pygame.K_y or joystick.JustPressedY():
                    self.info()
                if event.key == pygame.K_RETURN or joystick.JustPressedA():
                    self.money_sound.stop()
                    if self.top_selected:
                        self.done = True
                    else:
                        self.done = True
                        self.exit = True

    def info(self):
        display = self.display.copy()
        done = False
        rect = pygame.Rect(0, 0, 600, 400)
        rect.center = self.display.get_rect().center
        data = f"""
Shots fired: {len(self.acc)}
Shots hit: {self.acc.count(True)}
Shots missed: {self.acc.count(False)}
Accuracy: {self.acc_per2}%

Total attempts to beat this level:{self.lost}

Max Combo: {self.maxcombo}"""
        while not done:
            for event in pygame.event.get():
                joystick.Update(event)
                if not hasattr(event, "key"):
                    event.key = None
                if event.type == pygame.QUIT:
                    done = True
                if event.type == pygame.KEYUP or joystick.WasEvent():
                    if event.key == pygame.K_F2 or joystick.JustPressedLB():
                        screenshot.capture("WL_info", self.display)
                    if event.key in (pygame.K_q, pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE, pygame.K_y) or joystick.BackEvent() or joystick.GoEvent():
                        done = True
            self.display.blit(display, (0, 0))
            pygame.draw.rect(self.display, (40, 40, 40), rect)
            pygame.draw.rect(self.display, (255, 255, 0), rect, 1)
            for index, line in enumerate(data.split("\n")):
                retro_text((121, 142 + index * 14), self.display, 14, line, color=(0, 0, 0))
                retro_text((120, 140 + index * 14), self.display, 14, line)
            pygame.display.update()
        joystick.Reset()

    def draw(self):
        self.display.blit(self.images["background"], (0, 0))
        rect = pygame.Rect(0, 0, 400, 200)
        rect.center = self.display.get_rect().center
        self.display.blit(pygame.transform.scale(self.images[f"you_{self.mode}{self.frame}"], (400, 200)), rect)
        rect.move_ip(50, 0)
        pos = rect.left - 20, rect.bottom
        colors = [(255, 255, 175), (255, 255, 255)]
        if not self.top_selected:
            pos = rect.left - 20, rect.bottom + 20
            colors.reverse()
        self.display.blit(self.images["bullet"], pos)
        retro_text(rect.bottomleft, self.display, 14, self.text[0], anchor="topleft", color=colors[0])
        retro_text((rect.left, rect.bottom + 20), self.display, 14, self.text[1], anchor="topleft", color=colors[1])
        if self.mode == "won":
            retro_text((400, 25), self.display, 14, "Loot:", anchor="center")
            retro_text((400, 50), self.display, 14, round(self.money_old), anchor="center")
            retro_text((400, 75), self.display, 14, "Fast Victory Bonus", anchor="center")
            retro_text((400, 100), self.display, 14, round(self.bonus), anchor="center")
            retro_text((400, 125), self.display, 14, "Accuracy Bonus", anchor="center")
            retro_text((400, 150), self.display, 14, round(self.bonus1 * self.acc_per), anchor="center")
        retro_text((400, 165), self.display, 14, "Press <Y> for more info", anchor="center")

    def update(self):
        self.frame_time += self.time_passed
        if self.frame_time >= self.frame_rate and not self.anim_done:
            self.frame += 1
            self.frame_time = 0
        if self.frame > 50 and self.mode == "won":
            self.frame = 50
            self.anim_done = True
        if self.frame > 50 and self.mode == "lost":
            self.frame = 1
        if self.mode == "won":
            self.money_old -= (self.money_old - self.money_new) / 25
        if round(self.money_old) == round(self.money_new):
            self.money_sound.stop()
        pygame.display.update()
        self.time_passed = clock.tick(60) / 1000
