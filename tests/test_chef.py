
from pytest_mock_resources import create_mysql_fixture

from mestolo.chef import Chef
from mestolo.db import Base

from . import TEST_DIR


def session_fn(session):
    ...

db = create_mysql_fixture(Base, session_fn, session=True)

def test_chef_cooks(db):
    menu_path = TEST_DIR / 'data' / 'example_menu1.toml'
    c = Chef(menu_path, session=db)
    errors = c.cook()
    assert len(errors) == 0


def test_chef_handles_buggy_recipes(db):
    menu_path = TEST_DIR / 'data' / 'buggy_menu.toml'
    c = Chef(menu_path, session=db)
    errors = c.cook()
    assert len(errors) > 0
