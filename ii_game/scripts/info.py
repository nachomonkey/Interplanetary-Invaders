import pygame
from ii_game.scripts.retro_text import retro_text
from ii_game.scripts import joystick

pygame.init()

def display_info(display, images, item):
    clock = pygame.time.Clock()
    background = display.copy()
    done = False
    stuff_rect = pygame.Rect(0, 0, 500, 500)
    stuff_rect.center = display.get_rect().center
    icon_rect = pygame.Rect(0, 0, 100, 100)
    icon_rect.topleft = stuff_rect.move(5, 5).topleft
    data_rect = pygame.Rect(0, 0, 375, 480)
    data_rect.midtop = stuff_rect.move(50, 5).midtop
    while not done:
        for event in pygame.event.get():
            joystick.Update(event)
            if not hasattr(event, "key"):
                event.key = None
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYUP or joystick.WasEvent():
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_q,
                        pygame.K_SPACE, pygame.K_BACKSPACE, pygame.K_y) or joystick.GoEvent() or joystick.BackEvent():
                    done = True
        display.blit(background, (0, 0))
        pygame.draw.rect(display, (50, 50, 50), stuff_rect)
        pygame.draw.rect(display, (255, 255, 0), stuff_rect, 2)
        display.blit(pygame.transform.scale(images[item.icon], (100, 100)), icon_rect)
        pygame.draw.rect(display, (0, 0, 0), icon_rect, 1)
        pygame.draw.rect(display, (0, 0, 0), data_rect, 1)
        retro_text(data_rect.move(0, 10).midtop, display, 15, f'Information for "{item.title}"', anchor="midtop", font="impact")
        for y, line in enumerate(format_info(item).split("\n")):
            retro_text(data_rect.move(5, 40+14*y).topleft, display, 14, line, font="Sans")
        retro_text(stuff_rect.move(0, 2).midbottom, display, 14, "Press <Enter> to exit", anchor="midbottom", color=(0, 0, 0))
        retro_text(stuff_rect.midbottom, display, 14, "Press <Enter> to exit", anchor="midbottom")
        pygame.display.update()
        clock.tick(25)
    joystick.Reset()

def dry_init(v):
    return v([0, 0], [], None, True)

def format_bool(b):
    if b:
        return "Yes"
    return "No"

def format_info(item):
    data = f"Type: {item.type}\n\nRarity: {item.rarity*100}%\n\nCost: {item.cost} Loot"
    if item.type == "Item":
        data += f"""
Duration: {item.link().length} Seconds"""
    if item.type == "License":
        if item.title.startswith("SpaceTransport"):
            data += f"""
Maximum Mass: {item.max_mass} tons"""
    if item.type == "Vehicle":
        v = dry_init(item.link)
        data += f"""
Maximum Life: {v.max_health}
Maximum Shield: {v.max_shield}
Shots / second: {v.fire_per_sec}
Maximum Speed: {v.max_velocity} m/s
Rotating Barrel: {format_bool(v.rotate)}
Fires Beam: {format_bool(v.beam)}
Hover: {format_bool(v.hover)}
Mass: {v.mass} tons"""
    data += f"""\n\nDescription:\n{item.description}"""
    return data

