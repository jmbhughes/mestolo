import click

from .chef import Chef
from .menu import Menu


@click.command()
@click.argument('menu_path', type=click.Path(exists=True))
def main(menu_path):
    menu = Menu.load_toml(menu_path)
    chef = Chef(menu)
    chef.cook()
