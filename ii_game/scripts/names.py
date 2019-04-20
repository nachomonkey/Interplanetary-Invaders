import random


TITLES = ["Chief", 
        "General",
        "Colonel",
        "Major",
        "Captain",
        "Lieutenant",
        "Sergeant",
        "Tsar"]

NAMES = ["Squidbeard",
        "Kaffeehut",         # German for "Coffee house"
        "Feuerzueg",         # German for a cigarette lighter
        "Schlossecke",
        "Kartoffelgarten",   # German for "Potato Garden"
        "Bahnhof",           # German for "Train station"
        "Brotfoto",          # German for "Bread Photograph"
        "Zuckerbrot",        # German for "Sugarbread"
        "Hammerhead",
        "Blumenschuhe",      # German for "Flower Shoe"
        "Zuckerstra\N{latin small letter sharp s}e",  # German for "Sugar Street"
        "Entshuldigung",  # German for "Sorry"
        "Te\N{latin small letter u with diaeresis}er\N{latin small letter O with diaeresis}l",  # German for "Expensive Oil"
        ]

SINGLE_NAMES = [
        "Weltraum Spinne",   # German for "Space Spider"
        "Weltrekord Staubsauger", # German for "Planetary System Vacuum"
        "Acht Beine", # German for "Eight Legs"
]

def get_name():
    return random.choice(TITLES) + " " + random.choice(NAMES)


if __name__ == "__main__":
    print(get_name())
