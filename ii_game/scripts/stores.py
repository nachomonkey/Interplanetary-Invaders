import random
from copy import copy
import pygame
from ii_game.scripts.confirm import confirmExit
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts.maps import MapPoint
from ii_game.scripts.planets import PLANET_BY_NAME
from ii_game.scripts import saves
from ii_game.scripts import store_data
from ii_game.scripts.sound import Sound
from ii_game.scripts.utils import fix_path, divide_list
from ii_game.scripts.get_file import get_file
from ii_game.scripts.congrats import congrats
from ii_game.scripts.info import display_info
from ii_game.scripts import joystick

pygame.init()

def scanForStores(profile):
    stores = []
    for planet in profile["map"]:
        for p in profile["map"][planet]:
            if p.type == "store":
                stores.append(p)
    return stores

def confirmStores(profile, display, images):
    if profile["addNewStore"] <= 0:
        stores = []
        for p in profile["unlocked_planets"]:
            for point in profile["map"][p]:
                if point.type == "store":
                    stores.append((point, p))
        if stores:
            profile["addNewStore"] = random.randint(2, 4)
            store = random.choice(stores)
            store[0].store_data = None
            congrats(display, images, "store", PLANET_BY_NAME[store[1]])
    return profile

MAX_STORE_ITEM_LENGTH = 6

class StoreUI:
    def __init__(self, display, images, profile, profile_selected, map_point):
        self.display = display
        self.images = images
        self.profile = profile
        self.profile_selected = profile_selected
        center = display.get_rect().center
        self.main_rect = pygame.Rect(0, 0, 750, 550)
        self.main_rect.center = center
        self.list_rect = pygame.Rect(0, 0, 730, 300)
        self.list_rect.midbottom = self.main_rect.move(0, -10).midbottom
        self.buy_rect = pygame.Rect(0, 0, 355, 290)
        self.buy_rect.topleft = self.list_rect.move(5, 5).topleft
        self.inv_rect = self.buy_rect.copy()
        self.inv_rect.topleft = self.buy_rect.move(5, 0).topright
        self.item_rects = [self.buy_rect, self.inv_rect]
        self.items_rect = pygame.Rect(0, 0, 200, 40)
        self.items_rect.topright = self.main_rect.move(-5, 5).topright
        self.missiles_rect = self.items_rect.copy()
        self.missiles_rect.topleft = self.items_rect.move(0, 4).bottomleft
        self.licenses_rect = self.items_rect.copy()
        self.licenses_rect.topleft = self.missiles_rect.move(0, 4).bottomleft
        self.vehicles_rect = self.items_rect.copy()
        self.vehicles_rect.topleft = self.licenses_rect.move(0, 4).bottomleft
        self.drones_rect = self.items_rect.copy()
        self.drones_rect.topleft = self.vehicles_rect.move(0, 4).bottomleft
        self.money_rect = self.items_rect.copy()
        self.money_rect.w *= 1.35
        self.money_rect.midbottom = self.inv_rect.move(0, -10).midbottom
        self.data_rect = pygame.Rect(0, 0, 450, 225)
        self.data_rect.topleft = self.main_rect.move(5, 5).topleft
        self.rects = [self.items_rect, self.missiles_rect, self.licenses_rect, self.vehicles_rect, self.drones_rect]
        self.rect_names = ["Items", "Missiles", "Licenses", "Vehicles", "Drones"]
        self.rect_sel = 0
        self.done = False
        self.clock = pygame.time.Clock()
        self.items = store_data.getStuff("items", profile)
        self.missiles = {}
        self.licenses = store_data.getStuff("licenses", profile)
        self.vehicles = store_data.getStuff("vehicles", profile)
        self.drones = {}
        self.mapPoint = map_point
        if not hasattr(self.mapPoint, "store_data"):
            self.catagories = [self.items, self.missiles, self.licenses, self.vehicles, self.drones]
            self.mapPoint.store_data = self.catagories
        else:
            if self.mapPoint.store_data:
                self.catagories = self.mapPoint.store_data
            else:
                self.catagories = [self.items, self.missiles, self.licenses, self.vehicles, self.drones]
                self.mapPoint.store_data = self.catagories
        self.sel_num = [0, 0, 0, 0, 0]
        self.purchase_rect = pygame.Rect(0, 0, 175, 50)
        self.purchase_rect.midbottom = self.buy_rect.move(0, -5).midbottom
        self.exit_rect = pygame.Rect(0, 0, 275, 50)
        self.exit_rect.midbottom = self.purchase_rect.move(0, -5).midtop
        pygame.mixer.music.load(get_file(fix_path("audio/music/stores.mp3")))
        pygame.mixer.music.play(-1)
        
    def main(self):
        while not self.done:
            self.events()
            self.draw()
            self.update()
        saves.save_data(self.profile_selected, self.profile)
        pygame.mixer.music.fadeout(1000)

    def events(self):
        for event in pygame.event.get():
            joystick.Update(event)
            cat = self.catagories[self.rect_sel]
            click = False
            if not hasattr(event, 'key'):
                event.key = None
            if event.type == pygame.QUIT:
#                self.confirmExit()
                self.done = True
            if event.type == pygame.KEYUP or joystick.WasEvent():
                if (event.key == pygame.K_y or joystick.JustPressedY()) and cat:
                    selected = list(cat.keys())[self.sel_num[self.rect_sel]]
                    display_info(self.display, self.images, selected)
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                jwu = joystick.JustWentUp() or event.key in (pygame.K_w, pygame.K_UP)
                jwd = joystick.JustWentDown() or event.key in (pygame.K_s, pygame.K_DOWN)
                mod_sel = False
                if jwu or jwd:
                    sel = self.sel_num[self.rect_sel]
                    new_sel = copy(sel)
                    if jwd and sel + MAX_STORE_ITEM_LENGTH < len(cat):
                        mod_sel = True
                        new_sel += MAX_STORE_ITEM_LENGTH
                    if jwu and sel - MAX_STORE_ITEM_LENGTH >= 0:
                        mod_sel = True
                        new_sel -= MAX_STORE_ITEM_LENGTH
                    if mod_sel:
                        self.sel_num[self.rect_sel] = new_sel
                if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                    self.done = True
                if (jwu and not mod_sel) or joystick.JustPressedLT() or event.key == pygame.K_PAGEUP:
                    self.rect_sel -= 1
                if (jwd and not mod_sel) or joystick.JustPressedRT() or event.key == pygame.K_PAGEDOWN:
                    self.rect_sel += 1
                if self.rect_sel < 0:
                    self.rect_sel = 0
                if self.rect_sel >= len(self.rects):
                    self.rect_sel = len(self.rects) - 1
                cat = self.catagories[self.rect_sel] # REMEMBER: this line must be here!!!
                if event.key in (pygame.K_a, pygame.K_LEFT) or joystick.JustWentLeft():
                    self.sel_num[self.rect_sel] -= 1
                if event.key in (pygame.K_d, pygame.K_RIGHT) or joystick.JustWentRight():
                    self.sel_num[self.rect_sel] += 1
                if self.sel_num[self.rect_sel] < 0:
                    self.sel_num[self.rect_sel] = 0
                if self.sel_num[self.rect_sel] >= len(cat):
                    self.sel_num[self.rect_sel] = len(cat) - 1
                if event.key == pygame.K_RETURN or joystick.JustPressedA():
                    click = True
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.purchase_rect.collidepoint(pygame.mouse.get_pos()):
                    click = True
                if self.exit_rect.collidepoint(pygame.mouse.get_pos()):
                    self.done = True
            if click:
                self.purchase()

    def purchase(self):
        cat = self.catagories[self.rect_sel]
        if not cat:
            Sound(fix_path("audio/donk.wav")).play()
            return
        selected = list(cat.keys())[self.sel_num[self.rect_sel]]
        selected.planet = self.profile["planet"].name
        if self.profile["money"] >= selected.cost:
            Sound(fix_path("audio/purchase.wav")).play()
            cat[selected] -= 1
            if not cat[selected]:
                self.catagories[self.rect_sel].pop(selected)
            if self.sel_num[self.rect_sel] >= len(cat):
                self.sel_num[self.rect_sel] = len(cat) - 1
            if selected in self.profile["inventory"][self.rect_sel]:
                self.profile["inventory"][self.rect_sel][selected] += 1
            else:
                self.profile["inventory"][self.rect_sel][selected] = 1
            if selected.type == "Vehicle":
                self.profile["inventory"][self.rect_sel][selected] = self.profile["planet"].name
            self.profile["money"] -= selected.cost
        else:
            Sound(fix_path("audio/donk.wav")).play()

    def draw(self):
        self.display.blit(self.images["background"], (0, 0))
        pygame.draw.rect(self.display, (100, 100, 100), self.main_rect)

        pygame.draw.rect(self.display, (0, 0, 0), self.data_rect.move(2, 2))
        pygame.draw.rect(self.display, (75, 75, 75), self.data_rect)
        pygame.draw.rect(self.display, (0, 0, 0), self.data_rect, 1)

        pygame.draw.rect(self.display, (0, 0, 0), self.list_rect.move(2, 2))
        pygame.draw.rect(self.display, (75, 75, 75), self.list_rect)
        pygame.draw.rect(self.display, (0, 0, 0), self.list_rect, 1)

        for rect in self.item_rects:
            pygame.draw.rect(self.display, (0, 0, 0), rect.move(2, 2))
            pygame.draw.rect(self.display, (40, 40, 40), rect) 
            retro_text(rect.midtop, self.display, 15, "Available for purchase" if rect == self.buy_rect else "Your Inventory", anchor="midtop")
 
        pygame.draw.rect(self.display, (0, 0, 0), self.money_rect.move(2, 2))
        pygame.draw.rect(self.display, (75, 75, 75), self.money_rect)
        pygame.draw.rect(self.display, (0, 0, 0), self.money_rect, 1) 
        retro_text(self.money_rect.center, self.display, 15, f"{self.profile['money']} Loot", color=(255, 255, 175), anchor="center")

        for e, rect in enumerate(self.rects):
            color = (125, 125, 125)
            tcolor = (200, 200, 200)
            if e == self.rect_sel:
                color = (75, 75, 75)
                tcolor = (255, 255, 175)
                pygame.draw.rect(self.display, (0, 0, 0), rect.move(2, 2))
            pygame.draw.rect(self.display, color, rect)
            pygame.draw.rect(self.display, (0, 0, 0), rect, 1)
            retro_text(rect.center, self.display, 20, self.rect_names[e], color=tcolor, anchor="center")

        cat = self.catagories[self.rect_sel]
        for y, row in enumerate(divide_list(cat, MAX_STORE_ITEM_LENGTH)):
            for x, obj in enumerate(row):
                rect = pygame.Rect(0, 0, 50, 50)
                rect.topleft = self.buy_rect.move(5 + x * 55, 15 + y * 55).topleft
                trect = pygame.Rect(0, 0, 15, 15)
                c1, c2 = (50, 50, 50), (0, 0, 0)
                if y * MAX_STORE_ITEM_LENGTH + x == self.sel_num[self.rect_sel]:
                    c1, c2 = (50, 0, 0), (255, 0, 0)
                trect.bottomright = rect.bottomright
                pygame.draw.rect(self.display, c1, rect)
                self.display.blit(pygame.transform.scale(self.images[obj.icon], (50, 50)), rect)
                if not obj.type in ("License", "Vehicle"):
                    pygame.draw.rect(self.display, (150, 0, 0), trect)
                    pygame.draw.rect(self.display, (0, 0, 0), trect, 1)
                    retro_text(trect.center, self.display, 15, cat[obj], anchor="center")
                pygame.draw.rect(self.display, c2, rect, 1)

        cat2 = self.profile["inventory"][self.rect_sel]
        for y, row in enumerate(divide_list(cat2, MAX_STORE_ITEM_LENGTH)):
            for x, obj in enumerate(row):
                rect = pygame.Rect(0, 0, 50, 50)
                rect.topleft = self.inv_rect.move(5 + x * 55, 15 + y * 55).topleft
                trect = pygame.Rect(0, 0, 15, 15)
                trect.bottomright = rect.bottomright
                pygame.draw.rect(self.display, (50, 50, 50), rect)
                self.display.blit(pygame.transform.scale(self.images[obj.icon], (50, 50)), rect)
                if not obj.type in ("License", "Vehicle"):
                    pygame.draw.rect(self.display, (150, 0, 0), trect)
                    pygame.draw.rect(self.display, (0, 0, 0), trect, 1)
                    retro_text(trect.center, self.display, 15, cat2[obj], anchor="center")
                pygame.draw.rect(self.display, (0, 0, 0), rect, 1)
        if cat:
            selected = list(cat.keys())[self.sel_num[self.rect_sel]]
            pic_rect = pygame.Rect(0, 0, 100, 100)
            pic_rect.topleft = self.data_rect.move(5, 5).topleft
            pygame.draw.rect(self.display, (50, 50, 50), pic_rect)
            self.display.blit(pygame.transform.scale(self.images[selected.icon], (100, 100)), pic_rect)
            pygame.draw.rect(self.display, (0, 0, 0), pic_rect, 1)
            retro_text(pic_rect.move(225, 0).midtop, self.display, 14, selected.title, anchor="midtop", bold=True)
            retro_text(pic_rect.move(225, 20).midtop, self.display, 15, f"Cost: {selected.cost} Loot", anchor="midtop", bold=True)
            for e, l in enumerate(selected.description.split("\n")):
                retro_text(pic_rect.move(230, 35 + e * 12).midtop, self.display, 12, l, anchor="midtop")
            retro_text(self.data_rect.midbottom, self.display, 15, "Press <Y> for info", anchor="midbottom")

            color = (0, 175, 0)
            if self.purchase_rect.collidepoint(pygame.mouse.get_pos()):
                color = (0, 225, 0)
            if self.profile["money"] < selected.cost:
                color = (0, 10, 0)
            pygame.draw.rect(self.display, color, self.purchase_rect)
            pygame.draw.rect(self.display, (0, 0, 0), self.purchase_rect, 1)
            retro_text(self.purchase_rect.move(1, 1).center, self.display, 19, "Purchase", bold=True, anchor="center", color=(0, 0, 0))
            retro_text(self.purchase_rect.center, self.display, 19, "Purchase", bold=True, anchor="center", color=(100, 0, 255))
        color = (100, 0, 0)
        if self.exit_rect.collidepoint(pygame.mouse.get_pos()):
            color = (150, 0, 0)
        pygame.draw.rect(self.display, color, self.exit_rect)
        pygame.draw.rect(self.display, (0, 0, 0), self.exit_rect, 1)
        retro_text(self.exit_rect.move(1, 1).center, self.display, 15, "Press <ESC> to Exit", anchor="center", color=(0, 0, 0), font="sans")
        retro_text(self.exit_rect.center, self.display, 15, "Press <ESC> to Exit", anchor="center", font="sans")

    def update(self):
        pygame.display.update()
        self.clock.tick(60)
