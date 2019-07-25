#!/usr/bin/env python3

from setuptools import setup
from ii_game.scripts.utils import fixPath
from ii_game import __version__
import os, shutil, sys

with open("README.md", "r") as fh:
    long_description = fh.read()

def fmt(txt):
    return fixPath(txt.replace("ii_game/", "") + "/*")

img_data = []
for r, d, f in os.walk(fixPath("ii_game/images/bitmap")):
    if not fmt(r) in img_data:
        img_data.append(fmt(r))

if sys.platform == "linux" and not "sdist" in sys.argv:
    if os.path.exists("/usr/share/icons"):
        shutil.copyfile("ii_game/icon.png", "/usr/share/icons/ii_game-icon.png")
    if os.path.exists("/usr/share/applications"):
        shutil.copyfile("ii_game/ii_game.desktop", "/usr/share/applications/ii_game.desktop")

setup(
    name="Interplanetary Invaders",
    version=__version__,
    author="NachoMonkey",
    description="Pygame-made space-invaders-esc game where you battle alien spiders across the solar system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
    url="https://github.com/nachomonkey/interplanetary-invaders",
    install_requires=["setuptools", "pygame>=1.9.5"],
    packages=["ii_game", "ii_game.scripts"],
    package_data={"ii_game":["*.png", fixPath("fonts/*"), fixPath("music/*"), fixPath("audio/*"), fixPath("audio/music/*"), fixPath("data/*")] + img_data},
    entry_points={
        "console_scripts": [
            "interplanetary-invaders = ii_game.main:run",
            ]
        },
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
