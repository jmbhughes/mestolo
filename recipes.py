import random
import time


def recipe1():
    duration = random.randint(9, 10)
    duration = 15
    time.sleep(duration)
    return "b"


def recipe2():
    duration = random.randint(3, 10)
    duration = 15
    time.sleep(duration)
    return "c"


def recipe3(b=None, c=None):
    duration = random.randint(3, 10)
    duration = 15
    time.sleep(duration)
    return "d"
