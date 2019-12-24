import pygame

from ii_game.scripts.retro_text import retro_text
from ii_game.scripts import screenshot
from ii_game.scripts import joystick

pygame.init()

def congrats(display, images, mode, data, profile=None):
    """Display a screen for awarding achievements / unlocking planets"""
    done = False
    pf = 1
    pt = 0
    pfr = 1 / 25
    time_passed = 0
    total_time_passed = 0
    clock = pygame.time.Clock()
    if profile and mode == "ach":
        profile["money"] += data[2]
        profile["achievements"].append(data[0])
    while not done:
        for event in pygame.event.get():
            joystick.Update(event)
            if not hasattr(event, "key"):
                event.key = None
            if event.type == pygame.KEYDOWN or joystick.WasEvent():
                if event.key in (pygame.K_RETURN, pygame.K_ESCAPE) or joystick.GoEvent() or joystick.BackEvent():
                    done = True
                if event.key == pygame.K_F2 or joystick.JustPressedLB():
                    screenshot.capture("_congrats", display)
        display.blit(images["background"], (0, 0))
        if not mode == "store":
            retro_text((400, 100), display, 24, "Congratulations!", font = "impact", anchor = "center")
        stuff_rect = pygame.Rect(0, 0, 450, 350)
        if mode == "ach":
            stuff_rect.w *= 1.5
        stuff_rect.midtop = (400, 90)
        stuff_surf = pygame.Surface(stuff_rect.size)
        stuff_surf.fill((255, 0, 255))
        stuff_surf.set_alpha(50)
        display.blit(stuff_surf, stuff_rect)
        if mode == "planet" or mode == "store":
            rgba = ""
            if data.rgba:
                rgba = "RGBA"
            name = f"spinning{data.name}{rgba}{pf}"
            if not name in images:
                name = f"still_{data.name.lower()}"
            image = images[name]
            rect = pygame.Rect(0, 0, 100, 100)
            rect.center = (400, 200)
            display.blit(pygame.transform.scale(image, (100, 100)), rect)
            text = ""
            if not mode == "store":
                retro_text((400, 300), display, 14, f"You have unlocked Planet {data.name}", anchor = "center")
            else:
                retro_text((400, 300), display, 14, f"Restocked Store on {data.name}", anchor = "center")
            pt += time_passed
            if pt >= pfr:
                pf += 1
                pt = 0
            if pf > 25:
                pf = 1
        if mode == "ach":   # Short for achievement
            retro_text((400, 250), display, 17, f"{data[0]} Achievement Unlocked!", anchor = "center", font = "Sans")
            retro_text((400, 280), display, 15, data[1], anchor = "center", bold = True, font = "Sans")
            retro_text((400, 300), display, 15, f"Money Earned: {data[2]}", bold = True, font = "Sans", anchor = "center")
        if total_time_passed >= 15:
            done = True
        pygame.display.update()
        time_passed = clock.tick(60) / 1000
        total_time_passed += time_passed
