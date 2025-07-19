from __future__ import annotations

import abc
from typing import Iterable, Any, Type, List
import random


class SelectorABC(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __call__(self, inputs: List[Any]) -> List[Any]:
        pass

    def __rshift__(self, other: SelectorABC) -> CompoundSelector:
        return CompoundSelector([self, other])

class CompoundSelector(SelectorABC):
    def __init__(self, selectors: List[SelectorABC]):
        self._selectors = selectors

    def __call__(self, inputs: List[Any]) -> List[Any]:
        intermediate = inputs
        for selector in self._selectors:
            intermediate = selector(intermediate)
        return intermediate

    def __rshift__(self, other):
        return CompoundSelector(self._selectors + [other])

class IdentitySelector(SelectorABC):
    def __call__(self, inputs: List[Any]) -> List[Any]:
        return inputs

class FilterSelector(SelectorABC):
    def __init__(self, filter_func):
        self._filter = filter_func

    def __call__(self, inputs: List[Any]) -> List[Any]:
        # TODO: what if the filter method returns an error on the input?
        return [element for element in inputs if self._filter(element)]


class UseRandomSelector(SelectorABC):
    def __init__(self, count: int):
        self._count = count

    def __call__(self, inputs: List[Any]) -> List[Any]:
        if len(inputs) < self._count:
            raise RuntimeError(f"UseRandomSelector expects at least {self._count} elements in input.")
        return random.sample(inputs, self._count)

class SearchSelector(SelectorABC):
    def __init__(self, query, connection):
        self._query = query
        self._connection = connection

    def __call__(self, inputs: List[Any]) -> List[Any]:
        return self._connection(self._query)  # TODO : make this actually work in sqlalchemy
