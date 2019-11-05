
import pygame
import sys

from ii_game.scripts import joystick

pygame.init()

platform = "OS"

if sys.platform.startswith("win"):
    platform = "Windows"
if sys.platform == "linux":
    platform = "Linux"

def pause_menu(display, images, data, index, exit_lock = False):
    from ii_game.scripts.menu import Menu
    from ii_game.scripts.saves import save_data
    from ii_game.scripts.retro_text import retro_text
    joystick.Reset()
    background = display.copy()
    done = False
    sel = 0
    items = ["Resume", "Options", "Exit to Main Menu", f"Exit to {platform}"]
    old_items = items[:]
    stuff_rect = pygame.Rect(0, 0, 300, 400)
    stuff_rect.center = display.get_rect().center
    toMainMenu = False
    confirm = False
    while not done:
        for event in pygame.event.get():
            joystick.Update(event)
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                if not hasattr(event, "key"):
                    event.key = None
                if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                    done = True
                if event.key in (pygame.K_w, pygame.K_UP) or joystick.JustWentUp():
                    sel -= 1
                if event.key in (pygame.K_s, pygame.K_DOWN) or joystick.JustWentDown():
                    sel += 1
                if sel < 0:
                    sel = 0
                if sel >= len(items):
                    sel = len(items) - 1
                if event.key == pygame.K_RETURN or joystick.JustPressedA():
                    i = items[sel]
                    if confirm:
                        if i == "Save":
                            save_data(index, data)
                        if "Save" in i:
                            if not toMainMenu:
                                pygame.quit()
                                sys.exit()
                            done = True
                            return toMainMenu
                        if i == "Cancel":
                            confirm = False
                            toMainMenu = False
                            items = old_items
                    if i == "Resume":
                        done = True
                    if i == "Options":
                        m = Menu(display, images, True)
                        m.main()
                    if i == f"Exit to {platform}" and not exit_lock:
                        items = ["Cancel", "Save", "Don't Save"]
                        sel = 0
                        confirm = True
                    if i == "Exit to Main Menu" and not exit_lock:
                        toMainMenu = True
                        items = ["Cancel", "Save", "Don't Save"]
                        sel = 0
                        confirm = True
        display.blit(background, (0, 0))
        pygame.draw.rect(display, (0, 0, 0), stuff_rect)
        pygame.draw.rect(display, (255, 255, 0), stuff_rect, 1)
        for e, i in enumerate(items):
            color = (255, 255, 255)
            if e == sel:
                color = (255, 255, 175)
                display.blit(images["bullet"], (stuff_rect.left + 5, stuff_rect.top + 50 + e * 30))
            retro_text((stuff_rect.left + 10, stuff_rect.top + 50 + e * 30), display, 15, " " + i, color = color)
        pygame.display.update()
    return toMainMenu


