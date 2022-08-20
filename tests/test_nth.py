# pylama:ignore=D100,D101,D102,D103,D104,D105,D106,D107
# D100 : Missing docstring in public module
# D101 : Missing docstring in public class
# D102 : Missing docstring in public method
# D103 : Missing docstring in public function
# D104 : Missing docstring in public package
# D105 : Missing docstring in magic method
# D106 : Missing docstring in public nested class
# D107 : Missing docstring in __init__
import typing

import pytest

import nth

Converter: typing.TypeAlias = typing.Callable[[str], str]


def converter(f: typing.Callable[[str, bool], str], as_word: bool):
    def g(s: str):
        return f(s, as_word)

    return g


_c = converter(nth.cardinalize, False)
_C = converter(nth.cardinalize, True)
_o = converter(nth.ordinalize, False)
_O = converter(nth.ordinalize, True)

PARAMS = [
    ("1, 2, and 3", _C, "ONE, TWO, and THREE"),
]


@pytest.mark.parametrize("s,c,expect", PARAMS)
def test_convert(s: str, c: Converter, expect: str):
    assert c(s) == expect
