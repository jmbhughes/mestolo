import random
import time

from prefect import flow


def recipe1():
    duration = random.randint(9, 10)
    time.sleep(duration)

@flow
def recipe2():
    duration = random.randint(3, 10)
    time.sleep(duration)

@flow
def recipe3():
    duration = random.randint(3, 10)
    time.sleep(duration)
