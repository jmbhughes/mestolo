

import click

from .chef import Chef
from .menu import Menu
from .recipe import Recipe


def load_recipe(name, segment_config):
    return Recipe(name, **segment_config)


@click.command()
@click.argument('menu_path', type=click.Path(exists=True))
def main(menu_path):
    menu = Menu.load_toml(menu_path)
    chef = Chef(menu)
    chef.cook()


if __name__ == "__main__":
    main()
