"""Test nth paterns."""
# TODO:
# there's probably a way to have nested pytest parameterizations, but I can't figure it out.
# something like:
#
# @pytest.mark.parametrize("pattern,params", [(*_P, *_PARAMS)])
# def test_patterns(pattern: re.Pattern[str], params: typing.List[PatternParam]):
#     @pytest.mark.parametrize("n,expected", params):
#     def test_pattern(n: str, expected: bool):
#         ...
#
# Instead, for now, there's a declared test for every pattern with its params.

import re
import typing

import pytest

import nth


def _ns_params(
    n: int,
) -> typing.Tuple[typing.List[int], typing.List[int]]:
    should_match = [
        n,
        20 + n,
        30 + n,
        40 + n,
        50 + n,
        60 + n,
        70 + n,
        80 + n,
        90 + n,
        100 + n,
        120 + n,
        1000 + n,
        1020 + n,
        1100 + n,
        1120 + n,
        1130 + n,
    ]
    shouldnt_match = [
        *set(range(0, 10)) - {n},
        *set(range(10, 14)),
        *set(range(20, 24)) - {20 + n},
        *set(range(100, 104)) - {100 + n},
        *set(range(110, 114)),
        *set(range(1000, 1004)) - {1000 + n},
        *set(range(1010, 1014)),
        *set(range(1100, 1104)) - {1100 + n},
        *set(range(1110, 1114)),
    ]
    return (should_match, shouldnt_match)


def _pattern(p: str) -> typing.Pattern[str]:
    return re.compile(rf"\d*{p}", re.IGNORECASE)


def _params(
    should_match: typing.List[int],
    shouldnt_match: typing.List[int],
    suffix: str,
) -> typing.List[typing.Tuple[str, bool]]:
    return [
        *[(f"{n}{suffix}", True) for n in should_match],
        *[(f"{n}{suffix}", False) for n in shouldnt_match],
    ]


def _test_pattern(
    n: str,
    expected: bool,
    pattern: typing.Pattern[str],
):
    m = pattern.fullmatch(n)
    print(n)
    print(pattern)
    print(m, expected)
    assert (m is not None) == expected


_ONES_P = _pattern(nth.DIGIT_ORDINAL_ONES)
_ONES_PARAMS = _params(*_ns_params(1), "st")


@pytest.mark.parametrize("n,expected", _ONES_PARAMS)
def test_ones(n: str, expected: bool):
    """Test ones pattern (1st, 21st, etc.)."""
    _test_pattern(n, expected, _ONES_P)


_TWOS_P = _pattern(nth.DIGIT_ORDINAL_TWOS)
_TWOS_PARAMS = _params(*_ns_params(2), "nd")


@pytest.mark.parametrize("n,expected", _TWOS_PARAMS)
def test_twos(n: str, expected: bool):
    """Test twos pattern (2nd, 22nd, etc.)."""
    _test_pattern(n, expected, _TWOS_P)


_THREES_P = _pattern(nth.DIGIT_ORDINAL_THREES)
_THREES_PARAMS = _params(*_ns_params(3), "rd")


@pytest.mark.parametrize("n,expected", _THREES_PARAMS)
def test_threes(n: str, expected: bool):
    """Test threes pattern (3rd, 23rd, etc.)."""
    _test_pattern(n, expected, _THREES_P)


def _range_start(
    thousandths: int,
    hundredths: int,
    tens: int,
) -> int:
    return 1000 * thousandths + 100 * hundredths + 10 * tens


def _range(
    thousandths: int,
    hundredths: int,
    tens: int,
    lshift: int = 0,
    rshift: int = 10,
) -> range:
    start = _range_start(thousandths, hundredths, tens)
    return range(start + lshift, start + rshift)


_TEENS_P = _pattern(nth.DIGIT_ORDINAL_TEENS)
_TEENS_PARAMS = _params(
    [
        n
        for thousandths in range(2)
        for hundredths in range(2)
        for n in _range(thousandths, hundredths, 1, 1)
    ],
    [
        n
        for thousandths in range(2)
        for hundredths in range(2)
        for n in [
            *_range(thousandths, hundredths, 0),
            _range_start(thousandths, hundredths, 0),
            *_range(thousandths, hundredths, 2),
            *_range(thousandths, hundredths, 3),
        ]
    ],
    "th",
)


@pytest.mark.parametrize("n,expected", _TEENS_PARAMS)
def test_teens(n: str, expected: bool):
    """Test teens pattern (11th, 12th, ..., 19th, 111th, 112th, etc.)."""
    _test_pattern(n, expected, _TEENS_P)


_OTHERWISE_P = _pattern(nth.DIGIT_ORDINAL_OTHERWISE)
_OTHERWISE_PARAMS = _params(
    [
        n
        for thousandths in range(2)
        for hundredths in range(3)
        for n in [
            _range_start(thousandths, hundredths, 0),
            *_range(thousandths, hundredths, 0, 4, 11),
            *[
                n
                for tens in range(2, 10)
                for n in [
                    _range_start(thousandths, hundredths, tens),
                    *_range(thousandths, hundredths, tens, 4),
                ]
            ],
        ]
    ],
    [
        *[
            n
            for thousandths in range(2)
            for hundredths in range(3)
            for n in [
                *_range(thousandths, hundredths, 0, 1, 4),
                *_range(thousandths, hundredths, 1, 1),
                *[
                    n
                    for tens in range(2, 10)
                    for n in _range(thousandths, hundredths, tens, 1, 4)
                ],
            ]
        ]
    ],
    "th",
)


@pytest.mark.parametrize("n,expected", _OTHERWISE_PARAMS)
def test_otherwise(n: str, expected: bool):
    """Test otherwise pattern (4th, ..., 9th, 10th, ..., 14th, ... 19th, 20th, etc.)."""
    _test_pattern(n, expected, _OTHERWISE_P)


ST = "st"
ND = "nd"
RD = "rd"
TH = "th"
SUFFIXES = {ST, ND, RD, TH}


def _strict_params(
    should_match: typing.List[typing.Tuple[int, str]],
):
    return [
        *[(f"{n}{suffix}", True) for (n, suffix) in should_match],
        *[
            (f"{n}{bad_suffix}", False)
            for (n, suffix) in should_match
            for bad_suffix in SUFFIXES - {suffix}
        ],
    ]


def _strict_params_range(
    thousandths: int,
    hundredths: int,
):
    start = 1000 * thousandths + 100 * hundredths

    def _tens(tens: int):
        _start = start + 10 * tens
        return [
            (_start + 0, TH),
            (_start + 1, ST),
            (_start + 2, ND),
            (_start + 3, RD),
            *[(_start + n, TH) for n in range(4, 10)],
        ]

    return [
        *_tens(0),
        *[(start + n, TH) for n in range(10, 20)],
        *[p for tens in range(2, 10) for p in _tens(tens)],
    ]


STRICT_PARAMS = _strict_params(
    [
        p
        for thousandths in range(2)
        for hundredths in range(2)
        for p in _strict_params_range(thousandths, hundredths)
    ],
)


@pytest.mark.parametrize("n,expected", STRICT_PARAMS)
def test_strict(n: str, expected: bool):
    """Test full ordinal strict pattern."""
    _test_pattern(n, expected, nth.DIGIT_ORDINAL_STRICT_P)


# TODO:
# test non-strict (although this is also kinda handled in test_nth)
