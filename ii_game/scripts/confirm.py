import sys
import pygame
from ii_game.scripts import saves
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts.transition import transition
from ii_game.scripts import screenshot
from ii_game.scripts import joystick

pygame.init()

clock = pygame.time.Clock()

def confirmExit(display, profile, num):
    button_selected = 0
    buttons = ["Save + Exit", "Exit", "Cancel"]
    rect = pygame.Rect(0, 0, 150, 50)
    points = [(150, 400), (400, 400), (650, 400)]
    rect1, rect2, rect3 = rect.copy(), rect.copy(), rect.copy()
    rect1.midleft = points[0]
    rect2.center = points[1]
    rect3.midright = points[2]
    rects = [rect1, rect2, rect3]
    old_display = display.copy()
    surf2 = old_display.copy()
    surf2.fill((30, 30, 30))
    surf2.set_alpha(150)
    old_display.blit(surf2, (0, 0))
    while True:
        click = False
        for event in pygame.event.get():
            mpos = pygame.mouse.get_pos()
            joystick.Update(event)
            if not hasattr(event, 'key'):
                event.key = None
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                if event.key == pygame.K_F2 or joystick.JustPressedLB():
                    screenshot.capture(num, display)
            if event.type == pygame.MOUSEMOTION:
                for rect in rects:
                    if rect.collidepoint(mpos):
                        button_selected = rects.index(rect)
                        break
            if event.type == pygame.MOUSEBUTTONDOWN:
                for rect in rects:
                    if rect.collidepoint(mpos):
                        click = True
            if event.type == pygame.KEYUP or joystick.WasEvent():
                if event.key == pygame.K_ESCAPE or joystick.BackEvent():
                    return
                if event.key == pygame.K_LEFT or joystick.JustWentLeft():
                    button_selected -= 1
                if event.key == pygame.K_RIGHT or joystick.JustWentRight():
                    button_selected += 1
                if button_selected < 0:
                    button_selected = 0
                if button_selected > 2:
                    button_selected = 2
                if event.key == pygame.K_RETURN or joystick.JustPressedA():
                    click = True
        display.blit(old_display, (0, 0))
        retro_text((400, 302), display, 30, "Exit?", anchor="midbottom", bold=True, color=(0, 0, 0))
        retro_text((400, 300), display, 30, "Exit?", anchor="midbottom", bold=True)
        for n, rect in enumerate(rects):
            color = (75, 75, 75)
            tcolor = (255, 255, 255)
            if n == button_selected:
                color = (50, 50, 50)
                tcolor = (255, 255, 255)
            pygame.draw.rect(display, (0, 0, 0), rect.move(2, 2))
            pygame.draw.rect(display, color, rect)
            retro_text(rect.move(0, 2).center, display, 12, buttons[n], color = (0, 0, 0), anchor="center")
            retro_text(rect.center, display, 12, buttons[n], color = tcolor, anchor="center")
        pygame.display.update()
        clock.tick(10)
        if click:
            name = buttons[button_selected]
            if name == "Cancel":
                return
            if name == "Save + Exit":
                saves.save_data(num, profile)
                pygame.quit()
                sys.exit()
            if name == "Exit":
                transition(display, 5)
                pygame.quit()
                sys.exit()
