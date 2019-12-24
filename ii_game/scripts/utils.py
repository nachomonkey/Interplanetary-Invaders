"""Utility functions for Interplanetary Invaders"""

import os
import sys
import random

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

COLORS = {"header" : HEADER,
          "blue" : OKBLUE,
          "green" : OKGREEN,
          "warning" : WARNING,
          "fail" : FAIL,
          "endc" : ENDC,
          "bold" : BOLD,
          "underline" : UNDERLINE,
          }

def colorize(text, color):
    """Change some text's color for linux machines"""
    color = COLORS[str(color).lower()]
    if sys.platform != "linux":
        return text
    return f"{color}{text}{ENDC}"

def remove_doubles(list1):
    """Remove duplicate values from a list"""
    list2 = []
    for obj in list1:
        if not obj in list2:
            list2.append(obj)
    return list2

def fix_path(path):
    """Fix paths for Windows machines"""
    return path.replace("/", os.sep)

def num_or_rand(val, uniform=False):
    """If val is a list, use random.randint or uniform on it; else return val"""
    if type(val) in (list, tuple, set):
        if uniform:
            return random.uniform(val[0], val[1])
        return random.randint(val[0], val[1])
    return val

def divide_list(quotient, divisor):
    """Divide a list into multiple sublists"""
    result = []
    for e, i in enumerate(quotient):
        if not (e % divisor):
            result.append([])
        result[-1].append(i)
    return result
