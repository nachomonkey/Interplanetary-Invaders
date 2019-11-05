import os
import sys

HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

COLORS = {"header" : HEADER, "blue" : OKBLUE, "green" : OKGREEN,
"warning" : WARNING, "fail" : FAIL, "endc" : ENDC, "bold" : BOLD,
"underline" : UNDERLINE}

def colorize(text, color):
    color = COLORS[str(color).lower()]
    if sys.platform != "linux":
        return text
    return f"{color}{text}{ENDC}"

def remove_doubles(l):
    l2 = []
    for x in l:
        if not x in l2:
            l2.append(x)
    return l2

def fixPath(path):
    return path.replace("/", os.sep)

