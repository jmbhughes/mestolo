import os

from mestolo.chef import Chef
from mestolo.menu import Menu

from . import TEST_DIR


def test_chef_cooks():
    m = Menu.load_toml(os.path.join(TEST_DIR, 'data', 'example_menu1.toml'))
    c = Chef(m)
    errors = c.cook()
    assert len(errors) == 0


def test_chef_handles_buggy_recipes():
    m = Menu.load_toml(os.path.join(TEST_DIR, 'data', 'buggy_menu.toml'))
    c = Chef(m)
    errors = c.cook()
    assert len(errors) > 0
