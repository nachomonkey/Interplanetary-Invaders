#!/usr/bin/env python3

import sys

num = 24
if len(sys.argv) == 2:
    num = int(sys.argv[1])

mass = input(f"Enter planet's mass (10^{num} kg): ")

rad = input("Enter planet's radius (km): ")

GEE = 9.80665

GRAV_CONST = 6.67384 * 10 ** -11

grav = (GRAV_CONST) * (float(mass) * 10 ** num) / ((float(rad) * 1000) ** 2)

print("Planet's Gravity:")
print(round(grav, 5), "m/s^2")
print(round(grav * (3.048 * 10 ** -1), 5), "f/s^2")
print(round(grav / GEE, 5), "G")
