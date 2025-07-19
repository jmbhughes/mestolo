import pytest

from mestolo.selector import UseRandomSelector, FilterSelector, IdentitySelector


def test_use_random_selector_call():
    """Tests that the UseRandomSelector correctly down samples"""
    elements = [1, "a", "b", 3.4]
    selector = UseRandomSelector(2)

    out = selector(elements)

    # we get the right number of elements and they're all original elements
    assert len(out) == 2
    assert all([o in elements for o in out])

    # they're unique since all original elements were distinct
    assert len(set(out)) == 2

def test_use_random_selector_fails_on_too_few():
    """Tests that the UseRandomSelector fails if fewer than required elements provided."""
    elements = [1, "a", "b", 3.4]
    selector = UseRandomSelector(5)

    with pytest.raises(RuntimeError):
        selector(elements)

def test_filter_selector_call():
    """Tests that the FilterSelector correctly filters out elements."""
    elements = list(range(10))
    selector = FilterSelector(lambda x: x % 2 == 0)
    out = selector(elements)
    assert len(out) == 5
    assert out == [0, 2, 4, 6, 8]


def test_compound_selector_repeat_works():
    """Tests that the CompoundSelector correctly filters out elements."""
    elements = list(range(10))
    is_even = FilterSelector(lambda x: x % 2 == 0)
    is_small = FilterSelector(lambda x: x < 5)
    compound = is_even >> is_small
    out = compound(elements)
    assert out == [0, 2, 4]

def test_compound_selector_combines():
    """Tests that the CompoundSelector correctly combines to compound."""
    elements = list(range(10))
    is_even = FilterSelector(lambda x: x % 2 == 0)
    is_small = FilterSelector(lambda x: x < 5)
    is_random = UseRandomSelector(1)
    compound = is_even >> is_small >> is_random
    out = compound(elements)
    assert out[0] in [0, 2, 4]
    assert len(out) == 1

def test_identity_selector():
    """Tests that the IdentitySelector returns the input."""
    elements = list(range(10))
    out = IdentitySelector()(elements)
    assert out == elements
