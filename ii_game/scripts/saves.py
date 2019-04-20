import shelve
import os
from copy import deepcopy

from ii_game.scripts.get_file import get_file
from ii_game.scripts.utils import fixPath

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
        profile["finished_planets"] = data.get("finished_planets", [])
        profile["money_killed"] = data.get("money_killed", 0)
        profile["achievements"] = data.get("achievements", [])        # List of names of the achievements unlocked
        profile["inventory"] = data.get("inventory", [{}, {}, {TransportLicense1 : 1}, {StandardVehicle : 1}, {}])
        if len(profile["inventory"]) == 4:
            profile["inventory"].append({})
        profile["addNewStore"] = data.get("addNewStore", 5)
        m1 = profile["map"]
        M1 = deepcopy(m1)
        m2 = maps.AllMaps
        M2 = deepcopy(m2)
        for x in m1:
            for y in m1[x]:
                if not hasattr(y, "lost"):
                    y.lost = 0
        for x in m2:
            if not x in m1:
                m1[x] = m2[x]
                continue
            for Z in M1[x]:
                yes = False
                if hasattr(Z, "was_store"):
                    yes = Z.was_store
                if Z.type == "store" or yes:
                    M1[x].remove(Z)
            for Z in M2[x]:
                yes = False
                if hasattr(Z, "was_store"):
                    yes = Z.was_store
                if Z.type == "store" or yes:
                    M2[x].remove(Z)
            if len(M1[x]) != len(M2[x]):
                print(f"Invalid maps for profile {index}, attempting to rebuild")
                names = []
                for y in m2[x]:
                    for z in m1[x]:
                        c = False
                        if hasattr(z, "completed"):
                            c = z.completed
                        if y.name == z.name and ((not z.alien_flag) or z.type in ("spaceport", "info", "store")) and c:
                            names.append(y.old_name)
                m1[x] = m2[x]
                for z in m1[x]:
                    if z.name in names or z.next_name in names or z.old_name in names:
                        z.alien_flag = False
                        z.type = z.will_be
                        z.name = z.next_name
        for planet in profile["map"]:
            for point in profile["map"][planet]:
                if (point.type == "store" or point.will_be == "store") and not hasattr(point, "store_data"):
                    items = getStuff("items", profile)
                    missiles = {}
                    licenses = getStuff("licenses", profile)
                    vehicles = getStuff("vehicles", profile, planet)
                    drones = {}
                    point.store_data = [items, missiles, licenses, vehicles, drones]
    save_data(index, profile)
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
