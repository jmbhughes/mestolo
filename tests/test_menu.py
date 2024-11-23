
import pytest

from mestolo.error import MenuError
from mestolo.menu import Menu

from . import TEST_DIR


def test_read_menu_from_file():
    m = Menu.load_toml(TEST_DIR / 'data' / 'example_menu1.toml')
    assert isinstance(m, Menu)
    assert len(m.recipes) == 3
    assert m.max_simultaneous == 11
    assert m.refresh_delay == 3
    for i in range(1, 4):
        assert f"recipe{i}" in m.recipes
    assert m.get_recipe_for('b').name == 'recipe1'


def test_menu_error_raised_for_ingredient_with_no_recipe():
    with pytest.raises(MenuError):
        Menu.load_toml(TEST_DIR / 'data' / 'missing_recipe_menu.toml')
