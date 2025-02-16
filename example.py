from typing import Any, TypeAlias
import inspect
from collections import namedtuple

import networkx

IngredientConstraint = namedtuple("IngredientConstraint",
                                  ["name", "kind", "valid_interval", "count"])


class MyRecipe:
    def __init__(self, name, func):
        self.name = name
        self.func = func

    def __call__(self, *args, **kwargs):
        print(self.name)
        return self.func(*args, **kwargs)

class KindA:
    pass

class KindB:
    pass

class KindC:
    pass

class Source:
    pass

class Sink:
    pass

class Menu:
    def __init__(self):
        self.recipes = []

    def append(self, recipe):
        # TODO: if outputs already exist in the menu then you cannot add them again! only one recipe is allowed.
        self.recipes.append(recipe)

    def __repr__(self):
        return repr(self.recipes)

    def validate(self):
        graph = networkx.DiGraph()

        for r in self.recipes:
            sig = inspect.signature(r)
            if sig.return_annotation is None:
                raise RuntimeError("must have return annotation")

            if sig.parameters:
                for name, param in sig.parameters.items():
                    graph.add_node(param.annotation)
                    graph.add_edge(param.annotation, sig.return_annotation)
                    print(name, param.default)
            else:
                graph.add_edge("SOURCE", sig.return_annotation)

        return graph.edges

forward_direction = Menu()
backward_direction = Menu()

def recipe(menus, constraints, outputs, schedule, timeout=10*60):
    if not menus or menus is None:
        raise RuntimeError("Must have at least one menu")  # TODO: make a custom error

    if (constraints is None or not constraints) and schedule is None:
        raise RuntimeError("Must have a schedule if there are no constraints")

    def decorator_recipe(func):
        signature = inspect.signature(func)

        # all recipes must return something!
        if signature.return_annotation is None:
            raise RuntimeError("Must have return annotation")

        # make sure the function signature matches the decorator inputs
        required_signature_params = set(name for name, param in signature.parameters.items()
                                        if param.default is inspect.Parameter.empty)
        if set([constraint.name for constraint in constraints]) != required_signature_params:
            raise RuntimeError("Constraints must match the function signatures.")

        # try to add it to the menus
        if isinstance(menus, list):
            for menu in menus:
                menu.append(func)
        else:
            menus.append(func)
        return MyRecipe(func.__name__, func)
        #return func
    return decorator_recipe


@recipe(forward_direction, constraints=[], outputs="a", schedule="* * * * * *")
def make_a(special_option="hi there") -> KindA:
    return KindA()

from prefect import flow

@recipe(forward_direction, constraints=[], outputs="b", schedule="* * * * * *")
@flow
def make_b() -> KindB:
    return KindB()

@recipe(forward_direction, constraints=[], outputs="c", schedule="* * * * * *")
def make_c2() -> KindC:
    return KindC()

@recipe([forward_direction, backward_direction],
        constraints=[
            IngredientConstraint("source", "L0_a", None, 1),
            IngredientConstraint("calib1", "L0_b", "before", 1),
            IngredientConstraint("calib2", "L0_b", "after", 1)
        ],
        outputs="c",
        schedule=None)
def make_c(source: KindA, calib1: KindB, calib2: KindB) -> KindC:
    print(source, calib1, calib2)
    return KindC()

if __name__ == '__main__':
    print(forward_direction)
    print(backward_direction)
    #
    # print(forward_direction.validate())

    out = make_c(make_a(), make_b(), make_b())
    print(type(make_c))
    print(type(out))