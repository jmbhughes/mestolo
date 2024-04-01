import os
from datetime import datetime, timedelta

import toml
from freezegun import freeze_time

from mestolo.recipe import Recipe, ScheduledItem

from . import TEST_DIR


def test_recipe_loads_from_config():
    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r = Recipe.load_from_config("recipe1", config['recipe']['recipe1'])
    assert isinstance(r, Recipe)
    assert r.name == "recipe1"
    assert r.path == "./tests/data/example_recipes1.py"
    assert r.priority == 10
    assert not r.trigger
    assert r.delay == 1
    assert r.escalation_times == [5, 10, 15]
    assert r.escalation_values == [20, 30, 50]


def test_scheduled_item_creates():
    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r = Recipe.load_from_config("recipe1", config['recipe']['recipe1'])
    now = datetime.now()
    scheduled_item = ScheduledItem(now, r.priority, r)
    assert isinstance(scheduled_item, ScheduledItem)
    assert scheduled_item.schedule_time == now
    assert scheduled_item.current_priority == r.priority
    assert scheduled_item.recipe.name == "recipe1"
    assert scheduled_item.recipe.path == "./tests/data/example_recipes1.py"
    assert scheduled_item.recipe.priority == 10
    assert not scheduled_item.recipe.trigger
    assert scheduled_item.recipe.delay == 1
    assert scheduled_item.recipe.escalation_times == [5, 10, 15]
    assert scheduled_item.recipe.escalation_values == [20, 30, 50]


def test_scheduled_item_escalates():
    scheduled_time = datetime(2000, 1, 1, 0, 0, 0)

    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r = Recipe.load_from_config("recipe1", config['recipe']['recipe1'])
    scheduled_item = ScheduledItem(scheduled_time, r.priority, r)

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
    scheduled_item1 = ScheduledItem(scheduled_time, r1.priority, r1)
    scheduled_item2 = ScheduledItem(scheduled_time, r2.priority, r2)

    assert scheduled_item1 != scheduled_item2
    assert scheduled_item1 > scheduled_item2
    assert scheduled_item2 < scheduled_item1
    assert scheduled_item1 >= scheduled_item1
    assert scheduled_item1 <= scheduled_item1
    assert scheduled_item2 == scheduled_item2


def test_recipe_cooks():
    config = toml.load(os.path.join(TEST_DIR, "data", "example_menu1.toml"))
    r = Recipe.load_from_config("recipe3", config['recipe']['recipe3'])
    r.cook()
    assert True
