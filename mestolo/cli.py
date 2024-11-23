import argparse
import math
import multiprocessing as mp
import sys
import time

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

def main():
    parser = argparse.ArgumentParser(prog="mestolo")
    parser.add_argument("menu_path", type=str, help="Path to menu for running")
    args = parser.parse_args()

    menu = Menu.load_toml(args.menu_path)

    monitor_queue = mp.Queue()
    schedule_queue = mp.Queue()

    chef_process = mp.Process(target=run_chef, args=(menu, monitor_queue, schedule_queue))
    monitor_process = mp.Process(target=run_monitor, args=(menu, monitor_queue, schedule_queue))

    chef_process.start()
    time.sleep(1)  # wait a second so the chef is up and running
    monitor_process.start()

    chef_process.join()
    monitor_process.join()

    monitor_queue.close()
    schedule_queue.close()

    monitor_process.terminate()
    chef_process.terminate()
