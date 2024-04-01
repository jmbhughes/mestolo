import os

from mestolo.chef import Chef
from mestolo.menu import Menu

from . import TEST_DIR


def test_chef_cooks():
    m = Menu.load_toml(os.path.join(TEST_DIR, 'data', 'example_menu1.toml'))
    c = Chef(m)
    c.cook()
    assert True
