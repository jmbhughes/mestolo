from datetime import timedelta

import pytest

from mestolo.error import MenuError
from mestolo.recipe import Recipe, Menu, recipe
from mestolo.selector import IdentitySelector, UseRandomSelector


def test_recipe_menu_operations():
    m1 = Menu([])
    m2 = Menu([])

    r1 = recipe( {"a": IdentitySelector(), "b": IdentitySelector}, ["c"], timedelta(minutes=5), menus=[m1])(lambda a, b: "c")
    r2 = recipe( {"c": UseRandomSelector(5)}, ["d"], timedelta(minutes=5))(lambda c: "d")
    r1_2 = recipe({"b": IdentitySelector()}, ["c"], timedelta(minutes=5), menus=[m1])(lambda b: "c")

    assert r1("a", "b") == "c"
    assert m1.all_ingredients == {"a", "b", "c"}
    assert m2.all_ingredients == set()

    m2.add(r2)
    assert m2.all_ingredients == {"c", "d"}

    m1.add(r2)
    assert m1.all_ingredients == {"a", "b", "c", "d"}

    producer_a = recipe( {}, ["a"], timedelta(minutes=5))(lambda: "a")
    producer_b = recipe( {}, ["b"], timedelta(minutes=5))(lambda: "b")
    m3 = Menu([producer_a, producer_b, r1, r2])
    assert m3.all_ingredients == {"a", "b", "c", "d"}

    # order shouldn't matter
    m3 = Menu([r1, producer_a, producer_b, r2])
    m3.add(r1_2)
    assert m3.all_ingredients == {"a", "b", "c", "d"}
    assert len(m3.get_recipes_making("c")) == 2

def test_recipe_input_mismatch_fails():
    with pytest.raises(RuntimeError):
        recipe( {"a": IdentitySelector(), "b": IdentitySelector()}, ["c"], timedelta(minutes=5))(lambda crikey, b: "c")


def test_menu_fails_without_producers():
    with pytest.raises(MenuError):
        r1 = recipe({"a": IdentitySelector(), "b": IdentitySelector()}, ["c"], timedelta(minutes=5))(lambda a, b: "c")
        r2 = recipe({"c": UseRandomSelector(5)}, ["d"], timedelta(minutes=5))(lambda c: "d")
        Menu([r1, r2])
