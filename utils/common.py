# imports #
from sys import platform
import os

### 3 util functions. by github.com/notcooler ###
def getPlatform():
    plt = "unknown"
    if platform == "linux" or platform == "linux2":
        plt = "lin"
    elif platform == "win32":
        plt = "win"
    elif platform == "darwin":
        plt = "mac"
    return plt

def clear():
    if getPlatform() == "win":
        os.system('cls')
    elif getPlatform() == "lin" or getPlatform() == "mac":
        os.system('clear')
    else:
        pass

def setConsoleSize(*_x, **_y):
    x = '23'
    y = '78'
    if _x != None and len(_x) != 0: x = str(_x[0])
    if _y != None and len(_x) != 0: y = str(_x[1])
    if getPlatform() == "win":
        os.system(f'mode {x},{y}')
    elif getPlatform() == "lin" or getPlatform() == "mac":
        os.system(f'resize -s {y} {x}')
    else:
        pass

### end util functions ###