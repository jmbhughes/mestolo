import math
import multiprocessing as mp
import sys
import time

import click

from .chef import Chef
from .menu import Menu
from .monitor import create_app


def run_chef(menu, monitor_queue, schedule_queue):
    chef = Chef(menu, monitor_queue, schedule_queue)
    chef.cook()

def run_monitor(menu, monitor_queue, schedule_queue):
    app = create_app(menu, monitor_queue, schedule_queue)
    app.run_server(debug=False, port=8051)

    if not math.isinf(menu.duration):
        time.sleep(menu.duration)
        sys.exit(0)

@click.command()
@click.argument('menu_path', type=click.Path(exists=True))
def main(menu_path):
    print("DB CREATED")

    menu = Menu.load_toml(menu_path)

    monitor_queue = mp.Queue()
    schedule_queue = mp.Queue()

    chef_process = mp.Process(target=run_chef, args=(menu, monitor_queue, schedule_queue))
    monitor_process = mp.Process(target=run_monitor, args=(menu, monitor_queue, schedule_queue))

    chef_process.start()
    time.sleep(3)  # wait a few seconds so the chef is up and running
    monitor_process.start()
