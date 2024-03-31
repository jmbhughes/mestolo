import random
import time


def recipe1():
    duration = random.randint(0, 5)
    time.sleep(duration)
    print(f"1 cats {duration}")


def recipe2():
    duration = random.randint(0, 5)
    time.sleep(duration)
    print(f"2 dogs {duration}")


def recipe3():
    duration = random.randint(0, 5)
    time.sleep(duration)
    print(f"3 done {duration}")
