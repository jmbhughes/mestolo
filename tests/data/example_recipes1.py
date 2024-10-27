import random
import time


def recipe1():
    duration = random.randint(9, 10)
    time.sleep(duration)
    return 'b'

def recipe2(b=None):
    duration = random.randint(3, 10)
    time.sleep(duration)
    return 'c'

def recipe3(c=None):
    time.sleep(0.1)
    return 'd'

def recipe_buggy():
    raise RuntimeError("I'm a buggy recipe.")
