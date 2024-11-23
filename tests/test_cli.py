import os

from . import TEST_DIR


def test_cli_runs():
    menu_path = TEST_DIR / "data" / "example_menu1.toml"
    result = os.system(f"mestolo {menu_path}")
    assert result == 0
