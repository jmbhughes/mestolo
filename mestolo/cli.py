import toml

from multiprocessing import Process

import click

from .recipe import Recipe


def load_segment(name, segment_config):
    return Recipe(name, **segment_config)


@click.command()
@click.argument('system_path', type=click.Path(exists=True))
def main(system_path):
    system_config = toml.load(system_path)
    all_recipes = []
    process_count = 0
    for segment_name, segment_config in system_config['segment'].items():
        all_recipes.append(load_segment(segment_name, segment_config))

    print(all_recipes)

    for recipe in all_recipes:
        p = Process(target=recipe.run)
        process_count += 1
        p.start()


if __name__ == "__main__":
    main()
