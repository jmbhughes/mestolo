import multiprocessing as mp

import click

from .chef import Chef
from .menu import Menu
from .monitor import create_app


def run_chef(menu, monitor_queue):
    chef = Chef(menu, monitor_queue)
    chef.cook()

def run_monitor(refresh_rate, monitor_queue):
    app = create_app(refresh_rate, monitor_queue)
    app.run_server(debug=False, port=8051)

@click.command()
@click.argument('menu_path', type=click.Path(exists=True))
def main(menu_path):
    menu = Menu.load_toml(menu_path)

    monitor_queue = mp.Queue()

    chef_process = mp.Process(target=run_chef, args=(menu, monitor_queue))
    monitor_process = mp.Process(target=run_monitor, args=(menu.refresh_delay, monitor_queue))

    chef_process.start()
    monitor_process.start()

    chef_process.join()
    monitor_process.join()

    monitor_queue.close()
