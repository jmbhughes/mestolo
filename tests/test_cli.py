# import os
#
# from click.testing import CliRunner
#
# from mestolo.cli import main
#
# from . import TEST_DIR
#
#
# def test_cli_runs():
#     menu_path = os.path.join(TEST_DIR, "data", "example_menu1.toml")
#     runner = CliRunner()
#     result = runner.invoke(main, [menu_path])
#     assert result.exit_code == 0
