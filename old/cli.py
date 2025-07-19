import argparse
import multiprocessing as mp
import os
import subprocess
import time

from .chef import Chef
from .monitor import create_app

THIS_DIR = os.path.dirname(__file__)
app = create_app()
server = app.server

def run_chef(menu_path):
    chef = Chef(menu_path)
    chef.cook()

def main():
    parser = argparse.ArgumentParser(prog="mestolo")
    parser.add_argument("menu_path", type=str, help="Path to menu for running")
    args = parser.parse_args()

    # menu = Menu.load_toml(args.menu_path)

    # monitor_queue = mp.Queue()
    # schedule_queue = mp.Queue()

    chef_process = mp.Process(target=run_chef, args=(args.menu_path,))
    # monitor_process = mp.Process(target=run_monitor, args=(menu, monitor_queue, schedule_queue))
    monitor_process = subprocess.Popen(["gunicorn",
                                        "-b", "0.0.0.0:8051",
                                        "--chdir", THIS_DIR,
                                        "cli:server"])

    chef_process.start()
    time.sleep(1)  # wait a second so the chef is up and running
    # monitor_process.start()

    chef_process.join()
    # monitor_process.join()

    # monitor_queue.close()
    # schedule_queue.close()

    monitor_process.terminate()
    chef_process.terminate()
