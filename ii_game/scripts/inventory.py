import pygame

from ii_game.scripts.retro_text import retro_text
from ii_game.scripts import store_data
from ii_game.scripts.sound import Sound
from ii_game.scripts.utils import fix_path
from ii_game.scripts.info import display_info
from ii_game.scripts import joystick
from copy import copy

pygame.init()

class Inventory:
    def __init__(self, display, images, profile, sel = None, cat = None):
        self.display = display
        self.images = images
        self.profile = profile
        self.done = False
        self.clock = pygame.time.Clock()
        center = self.display.get_rect().center
        self.main_rect = pygame.Rect(0, 0, 750, 550)
        self.main_rect.center = center
        self.vehicle_rect = pygame.Rect(0, 0, 600, 75)
        self.vehicle_rect.midtop = self.main_rect.move(0, 100).midtop
        self.inv_rect = self.vehicle_rect.copy()
        self.inv_rect.midtop = self.vehicle_rect.move(0, 75).midbottom
        self.bring_rect = self.vehicle_rect.copy()
        self.bring_rect.midtop = self.inv_rect.move(0, 75).midbottom
        self.rects = [self.vehicle_rect, self.inv_rect, self.bring_rect]
        self.captions = ["Select Vehicle", "Your Items and Drones", "Items and Drones Brought"]
        self.selected = 2
        if not sel:
            self.sel_num = [0, 0, 0]
        else:
            self.sel_num = sel
        b3 = pygame.Rect(0, 0, 50, 50)
        b3.center = self.bring_rect.center
        b2 = b3.copy()
        b2.center = b3.move(-50, 0).center
        b1 = b3.copy()
        b1.center = b2.move(-50, 0).center
        b4 = b3.copy()
        b4.center = b3.move(50, 0).center
        b5 = b3.copy()
        b5.center = b4.move(50, 0).center
        b6 = b3.copy()
        b6.center = b5.move(50, 0).center
        b7 = b3.copy()
        b7.center = b1.move(-50, 0).center
        b8 = b3.copy()
        b8.center = b6.move(50, 0).center
        b9 = b3.copy()
        b9.center = b7.move(-50, 0).center
        b0 = b3.copy()
        b0.center = b8.move(50, 0).center
        if not store_data.ItemStorage10 in self.profile["inventory"][2]:
            self.b_rects = [[b1, None], [b2, None], [b3, None], [b4, None], [b5, None]]
        else:
            self.b_rects = [[b9, None], [b7, None], [b1, None], [b2, None], [b3, None],
[b4, None], [b5, None], [b6, None], [b8, None], [b0, None]]
        if not cat:
            self.catagories = [self.profile["inventory"][3].copy(), self.profile["inventory"][0].copy(), self.b_rects]
        else:
            self.catagories = cat
        self.button_selected = True
        self.button_rect = pygame.Rect(0, 0, 250, 50)
        self.button_rect.midbottom = self.display.get_rect().move(0, -35).midbottom
        if profile["planet"].name == "Venus" and store_data.VenusCrawler in self.catagories[0] and self.sel_num == [0, 0, 0]:
            self.sel_num[0] = list(self.catagories[0]).index(store_data.VenusCrawler)
        if profile["planet"].name == "Jupiter" and store_data.JupiterHover in self.catagories[0] and self.sel_num == [0, 0, 0]:
            self.sel_num[0] = list(self.catagories[0]).index(store_data.JupiterHover)

    def main(self):
        while not self.done:
            self.events()
            self.draw()
            self.update()
        self.profile["inventory"][3] = self.catagories[0]
        self.profile["inventory"][0] = self.catagories[1]
        return self.profile, self.catagories, list(self.catagories[0])[self.sel_num[0]].link, self.sel_num

    def getIfLocked(self, v):
        for l in self.profile["inventory"][2]:
            if l.max_mass >= v.link([0,0], 0, 0, True).mass:
                return False
        if self.profile["planet"].name == self.profile["inventory"][3][v]:
            return False
        return True

    def events(self):
        for event in pygame.event.get():
            click = False
            joystick.Update(event)
            if not hasattr(event, "key"):
                event.key = None
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button_rect.collidepoint(pygame.mouse.get_pos()):
                    click = True
            if event.type == pygame.KEYUP or joystick.WasEvent():
                if event.key == pygame.K_y or joystick.JustPressedY():
                    cat = self.catagories[self.selected]
                    sel = self.sel_num[self.selected]
                    if self.selected != 2:
                        item = list(cat.keys())[sel]
                    else:
                        item = cat[sel][1]
                    if item:
                        display_info(self.display, self.images, item)
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                if event.key in (pygame.K_UP, pygame.K_w) or joystick.JustWentUp():
                    if not self.button_selected:
                        self.selected -= 1
                    else:
                        self.button_selected = False
                if event.key in (pygame.K_DOWN, pygame.K_s) or joystick.JustWentDown():
                    self.selected += 1
                if self.selected < 0:
                    self.selected = 0
                if self.selected == len(self.rects):
                    self.selected = len(self.rects) - 1
                    self.button_selected = True
                if (event.key in (pygame.K_LEFT, pygame.K_a) or joystick.JustWentLeft()) and not self.button_selected:
                    self.sel_num[self.selected] -= 1
                if (event.key in (pygame.K_RIGHT, pygame.K_d) or joystick.JustWentRight()) and not self.button_selected:
                    self.sel_num[self.selected] += 1
                if self.sel_num[self.selected] < 0:
                    self.sel_num[self.selected] = 0
                if self.sel_num[self.selected] == len(self.catagories[self.selected]):
                    self.sel_num[self.selected] = len(self.catagories[self.selected]) - 1
                if (event.key == pygame.K_RETURN or joystick.JustPressedA()) and not self.button_selected:
                    cat = self.catagories[self.selected]
                    lcat = list(cat)
                    sel = self.sel_num[self.selected]
                    didSomething = False
                    if self.selected == 1:
                        for x in self.catagories[2]:
                            if x[1] == None:
                                if not lcat:
                                    return
                                didSomething = True
                                x[1] = lcat[sel]
                                if cat[lcat[sel]] == 1:
                                    cat.pop(lcat[sel])
                                    break
                                else:
                                    cat[lcat[sel]] -= 1
                                    break
                    if not didSomething:
                        Sound(fix_path("audio/donk.wav")).play()
                    if self.selected == 2 and cat[sel][1] != None:
                        done = False
                        for x in self.catagories[1]:
                            if x == cat[sel][1]:
                                self.catagories[1][x] += 1
                                done = True
                        if not done:
                            self.catagories[1][cat[sel][1]] = 1
                        cat[sel][1] = None
                if (event.key == pygame.K_RETURN or joystick.JustPressedA()) and self.button_selected:
                    click = True
            if click and not self.cannotContinue():
                self.done = True

    def draw(self):
        self.display.blit(self.images["background"], (0, 0))
        pygame.draw.rect(self.display, (100, 100, 100), self.main_rect)
        cat = self.catagories[self.selected]
        sel = self.sel_num[self.selected]
        for e, rect in enumerate(self.rects):
            try:
                list(self.catagories[e])[self.sel_num[e]]
            except IndexError:
                self.sel_num[e] -= 1
            bcolor = (0, 0, 0)
            color = (50, 50, 50)
            thickness = 1
            if e == self.selected and not self.button_selected:
                bcolor = (255, 0, 0)
                color = (125, 125, 125)
                thickness = 2
            pygame.draw.rect(self.display, (0, 0, 0), rect.move(2, 2))
            pygame.draw.rect(self.display, color, rect)
            pygame.draw.rect(self.display, bcolor, rect, thickness)
            retro_text(rect.move(0, -18).midtop, self.display, 15, self.captions[e], anchor="midbottom", color=(0, 0, 0))
            retro_text(rect.move(0, -20).midtop, self.display, 15, self.captions[e], anchor="midbottom")
            if self.catagories[e]:
                if self.captions[e] == "Items and Drones Brought":
                    title = copy(list(self.catagories[e])[self.sel_num[e]][1])
                    if title != None:
                        title = copy(title.title)
                else:
                    title = copy(list(self.catagories[e])[self.sel_num[e]].title)
                plus = ""
                if title:
                    title += " (press <Y> for info)"
                    retro_text(rect.move(0, -9).midtop, self.display, 15, title, anchor="midbottom", color=(0, 0, 0))
                    retro_text(rect.move(0, -10).midtop, self.display, 15, title, anchor="midbottom", color=(0, 0, 255))
            arrowrect = pygame.Rect(0, 0, 32, 32)
            arrowrect.midtop = self.inv_rect.move(0, 10).midbottom
            arrow = "down"
            if self.selected == 2:
                arrow = "up"
            self.display.blit(pygame.transform.scale(self.images[f"{arrow}arrow"], (32, 32)), arrowrect)
            for c in range(len(self.catagories)):
                for e, v in enumerate(self.catagories[c]):
                    msel = c == self.selected
                    if c == 2:
                        rect = v[0]
                        if v[1] == None:
                            v = None
                        else:
                            v = v[1]
                    else:
                        rect = pygame.Rect(0, 0, 50, 50)
                        rect.left = self.rects[c].left + 5 + e * 60
                        rect.centery = self.rects[c].centery
                    bcolor = (0, 0, 0)
                    color = (75, 75, 75)
                    thickness = 1
                    if msel and not self.button_selected:
                        color = (100, 100, 100)
                    if e == self.sel_num[c]:
                        bcolor = (255, 255, 0)
                        thickness = 2
                        if not msel or self.button_selected:
                            thickness = 1
                            bcolor = (0, 200, 0)
                    pygame.draw.rect(self.display, (0, 0, 0), rect.move(2, 2))
                    pygame.draw.rect(self.display, color, rect)
                    pygame.draw.rect(self.display, bcolor, rect, thickness)
                    if v:
                        self.display.blit(pygame.transform.scale(self.images[v.icon], (50, 50)), rect)
                        if c == 0:
                            if self.getIfLocked(v):
                                self.display.blit(self.images["nope"], rect)
                                if e == self.sel_num[c]:
                                    retro_text((400, 50), self.display, 15, "Higher Space Transport License level needed for this  vehicle", anchor="center", font="impact")
                                    retro_text((400, 65), self.display, 15, f"to be transported from {self.catagories[c][v]}", anchor="center", font="impact")
                    if self.captions[c] == "Your Items and Drones":
                        trect = pygame.Rect(0, 0, 15, 15)
                        trect.bottomright = rect.bottomright
                        pygame.draw.rect(self.display, (150, 0, 0), trect)
                        retro_text(trect.center, self.display, 15, self.catagories[c][v], anchor="center")
                        pygame.draw.rect(self.display, (0, 0, 0), trect, 1)
            color = (0, 100, 0)
            if self.button_selected or self.button_rect.collidepoint(pygame.mouse.get_pos()):
                color = (0, 230, 0)
            if self.cannotContinue():
                color = (100, 0, 0)
                if self.button_selected or self.button_rect.collidepoint(pygame.mouse.get_pos()):
                    color = (150, 0, 0)
            pygame.draw.rect(self.display, color, self.button_rect)
            retro_text(self.button_rect.move(0, 2).center, self.display, 15, "Continue Mission", anchor="center", color=(0, 0, 0))
            retro_text(self.button_rect.center, self.display, 15, "Continue Mission", anchor="center")

    def cannotContinue(self):
        if self.getIfLocked(list(self.catagories[0])[self.sel_num[0]]):
            return True
        return False

    def update(self):
        pygame.display.update()
        self.clock.tick(25)
