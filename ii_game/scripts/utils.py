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

def format_int(num):
    num = list(reversed(str(num)))
    spots = []
    first = len(num) % 3
    fdone = False
    if not first:
        fdone = True
    done = False
    e = 0
    while not done:
        print(e)
        if not fdone:
            if e == first:
                spots.append(e)
                fdone = True
        else:
            if (not len(spots) and e % 4) or (len(spots) and e - spots[-1] == 4):
                print("!")
                spots.append(e)
        if e == len(spots) + len(num) - 1:
            done = True
        e += 1
    print(spots)
    num = list(reversed(num))
    for e in spots:
        num.insert(e, ",")
    return "".join(num)

def remove_doubles(l):
    l2 = []
    for x in l:
        if not x in l2:
            l2.append(x)
    return l2

def fixPath(path):
    return path.replace("/", os.sep)


if __name__ == "__main__":
    print(format_int(10000000))
