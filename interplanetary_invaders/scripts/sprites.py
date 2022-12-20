#!/usr/bin/env python3
import sys
import os
import math
import re
import glob
import pygame

from interplanetary_invaders.scripts.utils import divide_list

pygame.init()

EXTRACT_DEST = "hacks/sprites"

CORNER_COLORS = [(255, 100, 1, 125), (255, 100, 1, 255)]
X_MARKER_COLOR = (255, 255, 0)
Y_MARKER_COLOR = (0, 255, 255)

def get_most_square_factors(num_entries):
    """Returns the set of factors of a given number
    that are the closest to each other"""
    factors = []
    x = 1

    while x <= num_entries:
        if not (num_entries % x):
            factors.append(x)
        x += 1

    factor_sets = []
    for x in factors:
        for y in factors:
            if x * y == num_entries and not (x, y) in factor_sets and not (y, x) in factor_sets:
                factor_sets.append((x, y))

    min_diff = math.inf
    result = [-1, -1]
    for x, y in factor_sets:
        diff = abs(x - y)
        if min_diff > diff:
            min_diff = diff
            result = (x, y)

    return result

def compress_surfaces(surfaces, filename=None):
    """Compress the given surfaces into a single image
    and exports to the given filename"""

    # Confirm all surfaces are the same size
    sprite_width = -1
    sprite_height = -1
    for surf in surfaces:
        if sprite_width < 0 or sprite_height < 0:
            sprite_width = surf.get_width()
            sprite_height = surf.get_height()
            assert sprite_width != 0 or sprite_height != 0, "Sprite dimensions must exceed 1 pixel"
            continue
        assert sprite_width == surf.get_width() and sprite_height == surf.get_height(), "All sprites must be the same size"

    sprite_columns, sprite_rows = get_most_square_factors(len(surfaces))
    result = pygame.Surface((sprite_columns * sprite_width + 1, sprite_rows * sprite_height + 1), pygame.SRCALPHA)
    result.set_at((0, 0), CORNER_COLORS[1])
    for x in range(1, sprite_columns):
        result.set_at((x * sprite_width + 1, 0), X_MARKER_COLOR)
    for y in range(1, sprite_rows):
        result.set_at((0, y * sprite_height + 1), Y_MARKER_COLOR)
    
    for y, row in enumerate(divide_list(surfaces, sprite_columns)):
        for x, surf in enumerate(row):
            result.blit(surf, (x * sprite_width + 1, y * sprite_height + 1))

    if filename:
        print(f"Exporting Spriresheet {filename}...")
        pygame.image.save(result, filename)

    return result

def extract_sprites(surface):
    surfaces = []

    sheet_width = surface.get_width()
    sheet_height = surface.get_height()

    assert sheet_width and sheet_height, "Sprite sheet dimensions must exceed 1 pixel"
    assert surface.get_at((0, 0)) in CORNER_COLORS, f"Invalid sprite sheet. Corner color is {surface.get_at((0, 0))}"

    sprite_width = -1
    sprite_height = -1

    # Get Sprite Width
    for x in range(1, surface.get_width()):
        if surface.get_at((x, 0)) == X_MARKER_COLOR:
            sprite_width = x - 1
            break

    # Get Sprite Height
    for y in range(1, surface.get_height()):
        if surface.get_at((0, y)) == Y_MARKER_COLOR:
            sprite_height = y - 1
            break

    if sprite_width == -1:
        sprite_width = sheet_width - 1

    if sprite_height == -1:
        sprite_height = sheet_height - 1

    sprite_columns = (sheet_width - 1) / sprite_width
    sprite_rows = (sheet_height - 1) / sprite_height

    assert sprite_columns.is_integer() and sprite_rows.is_integer(), "Invalid sprite sheet"
    sprite_columns = int(sprite_columns)
    sprite_rows = int(sprite_rows)

    for y in range(sprite_rows):
        for x in range(sprite_columns):
            rect = pygame.Rect(x * sprite_width + 1, y * sprite_height + 1, sprite_width, sprite_height)
            surfaces.append(surface.subsurface(rect).copy())

    return surfaces

def sort_enumerated(obj):
    return obj[0]

def scale_images(filename, dest, scale=1):
    print("Extracting...")
    surfs = []
    for e, surf in enumerate(extract_sprites(pygame.image.load(filename))):
        pygame.image.save(surf, dest + f"/sprite{str(e).zfill(4)}.png")
        surfs.append(pygame.transform.scale(surf, (int(surf.get_width() * scale), int(surf.get_height() * scale))))

    return

    ans = input("Are you sure you want to overwrite the image? [y/N]: ")

    if ans.lower() in ("y", "yes"):
        print("Exporting...")
        compress_surfaces(surfs, filename)
    else:
        print("Never mind")

def compress_images(files, filename=None):
    sorted_files = []
    for e, file in enumerate(files):
        split_index = len(re.split("[0-9]", file[:-4])[0])
        prefix = file[:-4][:split_index]
        num = file[:-4][split_index:]
        num = num.zfill(4)
        new_filename = prefix + num + ".png"
        sorted_files.append((new_filename, e))
    sorted_files.sort(key=sort_enumerated)

    finished_files = []
    for file, index in sorted_files:
        finished_files.append(files[index])

    surfaces = []
    for file in finished_files:
        surfaces.append(pygame.image.load(file))
    return compress_surfaces(surfaces, filename), surfaces

def main():
    """Test"""
    print("---------------")
    test_path = "interplanetary_invaders/images/bitmap/animations/player/zapper_death"
    if len(sys.argv) > 1:
        test_path = sys.argv[1]

    if not os.path.exists("hacks"):
        os.mkdir("hacks")

    if os.path.isdir(test_path):
        test_surf, surfaces = compress_images(glob.glob(test_path + "/*.png"), "hacks/spritesheet_test.png")
        
        print("Extracting...")
        surfaces2 = extract_sprites(test_surf)
        
        for e, surf in enumerate(surfaces):
            print(f"Testing sprite {e+1}")
            assert pygame.image.tostring(surf, "RGBA") == pygame.image.tostring(surfaces2[e], "RGBA"), f"Test failed!"
    else:
        if not os.path.exists(EXTRACT_DEST):
            os.mkdir(EXTRACT_DEST)
        scale_images(test_path, EXTRACT_DEST, float(sys.argv[2]) if len(sys.argv) > 2 else 1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
