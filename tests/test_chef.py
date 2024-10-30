import os

from mestolo.chef import Chef
from mestolo.db import create_db
from mestolo.menu import Menu

from . import TEST_DIR


def test_chef_cooks():
    create_db()
    m = Menu.load_toml(os.path.join(TEST_DIR, 'data', 'example_menu1.toml'))
    c = Chef(m)
    errors = c.cook()
    assert len(errors) == 0


def test_chef_handles_buggy_recipes():
    create_db()
    m = Menu.load_toml(os.path.join(TEST_DIR, 'data', 'buggy_menu.toml'))
    c = Chef(m)
    errors = c.cook()
    assert len(errors) > 0
