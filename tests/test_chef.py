from datetime import timedelta, datetime

from pytest_mock_resources import create_mysql_fixture

from mestolo.chef2 import Chef
from mestolo.db import Base, RecipeRunDB, RecipeRunState, RecipeDB


def session_fn_no_zombies(session):
    now = datetime.now()
    session.add(RecipeDB(name="test", inputs="None", outputs="None",
                         cadence_seconds=1, lookback_length_seconds=1, priority=1))
    for i in range(10):
        session.add(RecipeRunDB(recipe_name="test",
                                last_update=now,
                                status=RecipeRunState.cooking,
                                start_time=now))
        session.add(RecipeRunDB(recipe_name="test",
                                last_update=now, status=RecipeRunState.cooked,
                                start_time=now+timedelta(minutes=-i), end_time=now))

def session_fn_one_zombie(session):
    now = datetime.now()
    session.add(RecipeDB(name="test", inputs="None", outputs="None",
                         cadence_seconds=1, lookback_length_seconds=1, priority=1))
    for i in range(10):
        session.add(RecipeRunDB(recipe_name="test",
                                last_update=now,
                                status=RecipeRunState.cooking,
                                start_time=now))
        session.add(RecipeRunDB(recipe_name="test",
                                last_update=now, status=RecipeRunState.cooked,
                                start_time=now+timedelta(minutes=-i), end_time=now))

    session.add(RecipeRunDB(recipe_name="test", last_update=now, status=RecipeRunState.cooking,
                            start_time=now-timedelta(days=100)))

db = create_mysql_fixture(Base, session_fn_no_zombies, session=True)
db_zombie = create_mysql_fixture(Base, session_fn_one_zombie, session=True)

def test_no_zombie_detection(db):
    chef = Chef([], 10, db)
    zombie_count = len(chef.check_for_zombies("test"))
    assert zombie_count == 0

def test_one_zombie_detection(db_zombie):
    chef = Chef([], 10, db_zombie)
    zombie_count = len(chef.check_for_zombies("test"))
    assert zombie_count == 1

# def test_chef_cooks(db):
#     menu_path = TEST_DIR / 'data' / 'example_menu1.toml'
#     c = Chef(menu_path, session=db)
#     errors = c.cook()
#     assert len(errors) == 0
#
#
# def test_chef_handles_buggy_recipes(db):
#     menu_path = TEST_DIR / 'data' / 'buggy_menu.toml'
#     c = Chef(menu_path, session=db)
#     errors = c.cook()
#     assert len(errors) > 0
