import shelve
import os
from copy import deepcopy

from ii_game.scripts.get_file import get_file
from ii_game.scripts.utils import fix_path

debugMode = True

DATA_PATH = "data/"

DATA_PATH = get_file(DATA_PATH)

if not os.path.exists(DATA_PATH):
    os.mkdir(DATA_PATH)
    if debugMode:
        print(f"Directory \"{DATA_PATH}\" found missing!")

def load_profile(index):
    profile = {}
    if debugMode:
        if not os.path.exists(f"{DATA_PATH}/profile{index}"):
            print(f"Profile {index} missing!")
    with shelve.open(f"{DATA_PATH}/profile{index}") as data:
        profile["money"] = data.get("money", 0)
        profile["hiscore"] = data.get("hiscore", 0)
        profile["moons_locked"] = data.get("moons_locked", True)
        profile["exoplanets_locked"] = data.get("exoplanets_locked", True)
        profile["planet"] = data.get("planet", planets.Earth)
        profile["new"] = data.get("new", True)
        profile["map"] = data.get("map", maps.AllMaps)
        profile["points"] = data.get("points", maps.SavedPoints)
        profile["unlocked_planets"] = data.get("unlocked_planets", ["Earth"])
        profile["money_killed"] = data.get("money_killed", 0)
        profile["achievements"] = data.get("achievements", [])        # List of names of the achievements unlocked
        profile["inventory"] = data.get("inventory", [{}, {}, {TransportLicense1 : 1}, {StandardVehicle : 1}, {}])
        if len(profile["inventory"]) == 4:
            profile["inventory"].append({})
        profile["addNewStore"] = data.get("addNewStore", 5)
        profile["version"] = data.get("version", "?")
    return profile

def load_options():
    options = {}
    if debugMode:
        if not os.path.exists(f"{DATA_PATH}/options"):
            print("No options data file found!")
    with shelve.open(f"{DATA_PATH}/options") as data:
        options["volume"] = data.get("volume", 1)
        options["cache_screen_shots"] = data.get("cache_screen_shots", False)
        options["fullscreen"] = data.get("fullscreen", False)
    return options

def save_data(index, profile):
    filename = f"{DATA_PATH}/options"
    if index != "options":
        filename = f"{DATA_PATH}/profile{index}"
    with shelve.open(filename) as data:
        for x in profile:
            data[x] = profile[x]

from ii_game.scripts import planets
from ii_game.scripts import maps
from ii_game.scripts.store_data import TransportLicense1, StandardVehicle, getStuff
