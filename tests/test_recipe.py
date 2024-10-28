import multiprocessing
import os
from datetime import datetime, timedelta

import toml
from freezegun import freeze_time

from mestolo.datetime import DateTimeInterval
from mestolo.ingredients import IngredientConstraint, ScheduledIngredient
from mestolo.recipe import Recipe

from . import TEST_DIR


def test_recipe_loads_from_config():
    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r = Recipe.load_from_config("recipe1", config['recipe']['recipe1'])
    assert isinstance(r, Recipe)
    assert r.name == "recipe1"
    assert r.path == "./tests/data/example_recipes1.py"
    assert r.priority == 10
    assert not r.trigger
    assert r.schedule == "* * * * * *"
    assert r.escalation_times == [5, 10, 15]
    assert r.escalation_values == [20, 30, 50]


def test_scheduled_item_creates():
    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r = Recipe.load_from_config("recipe1", config['recipe']['recipe1'])
    now = datetime.now()
    scheduled_item = ScheduledIngredient(now, r.priority, r, {},
                                         IngredientConstraint(r.ingredient, DateTimeInterval(None, None)))
    assert isinstance(scheduled_item, ScheduledIngredient)
    assert scheduled_item.schedule_time == now
    assert scheduled_item.current_priority == r.priority
    assert scheduled_item.recipe.name == "recipe1"
    assert scheduled_item.recipe.path == "./tests/data/example_recipes1.py"
    assert scheduled_item.recipe.priority == 10
    assert not scheduled_item.recipe.trigger
    assert scheduled_item.recipe.schedule == "* * * * * *"
    assert scheduled_item.recipe.escalation_times == [5, 10, 15]
    assert scheduled_item.recipe.escalation_values == [20, 30, 50]


def test_scheduled_item_escalates():
    scheduled_time = datetime(2000, 1, 1, 0, 0, 0)

    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r = Recipe.load_from_config("recipe1", config['recipe']['recipe1'])
    scheduled_item = ScheduledIngredient(scheduled_time, r.priority, r, {},
                                         IngredientConstraint(r.ingredient, DateTimeInterval(None, None)))

    with freeze_time(scheduled_time) as frozen_datetime:
        assert scheduled_item.current_priority == 10

        frozen_datetime.move_to(scheduled_time + timedelta(seconds=4))
        scheduled_item.escalate_priority()
        assert scheduled_item.current_priority == 10

        frozen_datetime.move_to(scheduled_time + timedelta(seconds=6))
        scheduled_item.escalate_priority()
        assert scheduled_item.current_priority == 20

        frozen_datetime.move_to(scheduled_time + timedelta(seconds=11))
        scheduled_item.escalate_priority()
        assert scheduled_item.current_priority == 30

        frozen_datetime.move_to(scheduled_time + timedelta(seconds=16))
        scheduled_item.escalate_priority()
        assert scheduled_item.current_priority == 50


def test_scheduled_item_comparison():
    scheduled_time = datetime(2000, 1, 1, 0, 0, 0)
    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r1 = Recipe.load_from_config("recipe1", config['recipe']['recipe1'])
    r2 = Recipe.load_from_config("recipe2", config['recipe']['recipe2'])
    scheduled_item1 = ScheduledIngredient(scheduled_time, r1.priority, r1, {},
                                          IngredientConstraint(r1.ingredient, DateTimeInterval(None, None)))
    scheduled_item2 = ScheduledIngredient(scheduled_time, r2.priority, r2, {},
                                          IngredientConstraint(r2.ingredient, DateTimeInterval(None, None)))

    assert scheduled_item1 != scheduled_item2
    assert scheduled_item1 > scheduled_item2
    assert scheduled_item2 < scheduled_item1
    assert scheduled_item1 >= scheduled_item1
    assert scheduled_item1 <= scheduled_item1
    assert scheduled_item2 == scheduled_item2


def test_recipe_cooks():
    cooked_queue = multiprocessing.Queue()
    error_queue = multiprocessing.Queue()

    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r = Recipe.load_from_config("recipe3", config['recipe']['recipe3'])
    r.cook([], None, cooked_queue, error_queue)
    assert True
