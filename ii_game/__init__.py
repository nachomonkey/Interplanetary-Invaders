import os

__myname__ = "Interplanetary Invaders"
__title__ = "Interplanetary Invaders"
__author__ = "NachoMonkey"
__version__ = "0.0.5.3"
__minimum_version__ = (3, 7)
__maximum_version = (3, 8)

if os.path.abspath(".").endswith("interplanetary-invaders"):
    print("Running in Dev Mode")
