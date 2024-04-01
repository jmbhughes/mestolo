import os

from mestolo.menu import Menu

from . import TEST_DIR


def test_read_menu_from_file():
    m = Menu.load_toml(os.path.join(TEST_DIR, 'data', 'example_menu1.toml'))
    assert isinstance(m, Menu)
    assert len(m.recipes) == 3
    assert m.max_simultaneous == 11
    assert m.refresh_delay == 3
    for i in range(1, 4):
        assert f"recipe{i}" in m.recipes
