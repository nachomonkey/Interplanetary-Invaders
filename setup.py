#!/usr/bin/env python3

from setuptools import setup
from interplanetary_invaders.scripts.utils import fix_path
from interplanetary_invaders.scripts.get_file import get_file, SOUND_PATH
from interplanetary_invaders import __version__
import os, shutil, sys

with open("README.md", "r") as fh:
    long_description = fh.read()

def fmt(txt):
    return fix_path(txt.replace("interplanetary_invaders/", "") + "/*")

img_data = []

for r, d, f in os.walk(fix_path("interplanetary_invaders/images/bitmap")):
    if not fmt(r) in img_data:
        img_data.append(fmt(r))

if "install" in sys.argv and __name__ == "__main__":
    if sys.platform == "linux" and not "sdist" in sys.argv and not os.getuid():
        if os.path.exists("/usr/share/icons"):
            shutil.copyfile("interplanetary_invaders/icon.png", "/usr/share/icons/interplanetary_invaders-icon.png")
        if os.path.exists("/usr/share/applications"):
            shutil.copyfile("interplanetary_invaders/interplanetary_invaders.desktop", "/usr/share/applications/interplanetary_invaders.desktop")

setup(
    name="Interplanetary Invaders",
    version=__version__,
    author="NachoMonkey",
    description="Space-invaders-esc game where you battle alien spiders across the solar system",
    long_description=long_description,
    long_description_content_type="text/markdown",
    zip_safe=False,
    url="https://github.com/nachomonkey/interplanetary-invaders",
    install_requires=["setuptools", "pygame>=1.9.6", "humanize>=0.5.0"],
    packages=["interplanetary_invaders", "interplanetary_invaders.scripts"],
    package_data={"interplanetary_invaders":["*.png", fix_path("fonts/*"), fix_path("music/*"), fix_path("audio/*"), fix_path("audio/music/*"), fix_path("data/*")] + img_data},
    entry_points={
        "console_scripts": [
            "interplanetary-invaders = interplanetary_invaders.main:run",
            ]
        },
    python_requires=">=3.7",
    classifiers=[
        "Operating System :: OS Independent",
    ],
)
