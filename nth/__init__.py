"""Utilities for handling ordinal and cardinal numbers.

- nth_int
    - to_cardinal
    - to_ordinal

- nth_str
    - is_cardinal
    - is_ordinal

    - decimal_to_cardinal
    - decimal_to_ordinal

    - cardinalize
    - ordinalize
"""
from __future__ import annotations

import enum
import itertools
import logging
import operator
import os
import re
import typing
from contextlib import suppress
from dataclasses import dataclass

from .lookups import (
    CARDINAL_TO_INT,
    INT_TO_CARDINAL,
    INT_TO_ORDINAL,
    INT_TO_PERIOD,
    ORDINAL_TO_INT,
    PERIOD_TO_INT,
)

logger = logging.getLogger(__name__)
if (log_level_str := os.environ.get("NTH_LEVEL")) is not None:
    if log_level_str.isdecimal():
        log_level = int(log_level_str)
    else:
        log_level = logging.getLevelName(log_level_str)
    logger.setLevel(log_level)


class Period(typing.NamedTuple):
    """A period for ordinal/cardinal representation of a number.

    With regards to numbers, a period is a grouping of digits that makes representing
    numbers easier, and corresponds to a place value within the number. The first period
    represents the first three least significant digits, the second or thousandths period
    represents the thousandths digits, and so on. For example, 12345 has zeroth period 345
    written as "three hundred forty-five" and thousandths period 12 written as "twelve
    thousand"; together "twelve thousand three hundred forty five."

    In Python, number literals can contain underscore characters; these are often used to
    denote periods. e.g. 12_345.

    Fields:
        period: Index of the period (0: zeroth, 1: thousandths, etc.)
        digits: Digits for the period
    """

    period: int
    digits: int

    def to_cardinal(self) -> str:
        """Construct the cardinal representation of the period."""
        p = "" if self.period == 0 else " " + INT_TO_PERIOD[self.period]
        q, r = divmod(self.digits, 100)
        if q > 0:
            if r > 0:
                # e.g. ONE HUNDRED ONE
                _q = _encode_hecto(q, INT_TO_CARDINAL)
                _r = _encode_hecto(r, INT_TO_CARDINAL)
                return f"{_q} HUNDRED {_r}{p}"
            else:
                # e.g. ONE HUNDRED
                _q = _encode_hecto(q, INT_TO_CARDINAL)
                return f"{_q} HUNDRED{p}"
        else:
            # e.g. ONE; TEN; ONE THOUSAND
            _r = _encode_hecto(r, INT_TO_CARDINAL)
            return f"{_r}{p}"

    def to_ordinal(self) -> str:
        """Construct the ordinal representation of the period."""
        p = "" if self.period == 0 else " " + INT_TO_PERIOD[self.period]
        q, r = divmod(self.digits, 100)
        if q > 0:
            # e.g. ONE HUNDRED FIRST; ONE THOUSAND ONE HUNDRED ELEVENTH
            if r > 0:
                _q = _encode_hecto(q, INT_TO_CARDINAL)
                _r = _encode_hecto(r, INT_TO_ORDINAL)
                return f"{_q} HUNDRED {_r}{p}"
            else:
                _q = _encode_hecto(q, INT_TO_CARDINAL)
                return f"{_q} HUNDRED{p}TH"
        elif p:
            # e.g. ONE THOUSANDTH
            _r = _encode_hecto(r, INT_TO_CARDINAL)
            return f"{_r}{p}TH"
        else:
            # e.g. TENTH; ONE THOUSAND TENTH
            _r = _encode_hecto(r, INT_TO_ORDINAL)
            return f"{_r}{p}"

    @staticmethod
    def periods_from_int(n: int) -> typing.Iterator[Period]:
        """Iterate periods of number from least to most significant."""
        period = 0
        while n > 0:
            digits = n % 1000
            if digits != 0:
                yield Period(period, digits)
            n //= 1000
            period += 1

    def __str__(self) -> str:
        """As string (cardinal representation)."""
        return self.to_cardinal()


def _encode_hecto(n: int, lookup: typing.Dict[int, str]) -> str:
    """Encode an integer strictly between zero and a hundred.

    Arguments:
        n: Integer to encode.
        lookup: Lookup table (either INT_TO_CARDINAL or INT_TO_ORDINAL).

    Raises:
        AssertionError: If n <= 0 or n >= 100.
    """
    assert n > 0 and n < 100
    if s := lookup.get(n):
        return s
    deca = n % 10
    hundreds = INT_TO_CARDINAL[n - deca]
    hecto = _encode_hecto(deca, lookup)
    return f"{hundreds}-{hecto}"


def int_to_cardinal(n: int) -> str:
    """Convert integer to cardinal form."""
    if n == 0:
        return "zero"
    periods = list(Period.periods_from_int(n))
    return " ".join(map(str, reversed(periods)))


def int_to_ordinal(n: int) -> str:
    """Convert integer to ordinal form."""
    if n == 0:
        return "zeroth"
    periods = list(Period.periods_from_int(n))
    periods.reverse()
    ordinal_period = periods.pop()
    return " ".join(itertools.chain(map(str, periods), (ordinal_period.to_ordinal(),)))


def _ordinal_suffix(n: int) -> typing.Optional[str]:
    if 10 < (n % 100) < 20:
        return "TH"
    d = n % 10
    if d == 1:
        return "ST"
    elif d == 2:
        return "ND"
    elif d == 3:
        return "RD"
    else:
        return "TH"


def int_to_digit_ordinal(n: int) -> str:
    suffix = _ordinal_suffix(n)
    return f"{n}{suffix}"


DECIMAL_ORDINAL_NONSTRICT_P = re.compile(r"\b(\d+)(ST|ND|RD|TH)\b", re.IGNORECASE)


def fix_decimal_ordinal(s: str) -> str:
    if m := DECIMAL_ORDINAL_NONSTRICT_P.fullmatch(s):
        n = int(m.group(1))
        suffix = _ordinal_suffix(n)
        return f"{n}{suffix}"
    return s


def is_decimal_ordinal(s: str, strict: bool = False) -> bool:
    """Is string a decimal-ordinal number?

    True examples:
    - "123RD"
    - "123TH" only if strict=True

    False examples:
    - "ONE HUNDRED TWENTY-THIRD" this is word-ordinal, not decimal-ordinal
    """
    if m := DECIMAL_ORDINAL_NONSTRICT_P.fullmatch(s):
        if not strict:
            return True
        n, suffix = typing.cast(tuple[str, str], m.groups())
        return _ordinal_suffix(int(n)) == suffix
    return False


def contains_decimal_ordinal(s: str, strict: bool = False) -> bool:
    """Does strint contain any decimal-ordinal words?"""
    return any(
        map(
            lambda w: is_decimal_ordinal(w, strict),
            map(re.Match[str].group, re.finditer(r"\S+", s)),
        )
    )


# strict patterns for matching digit ordinals
DECIMAL_ORDINAL_ONES = r"(?<!1)1ST"
DECIMAL_ORDINAL_TWOS = r"(?<!1)2ND"
DECIMAL_ORDINAL_THREES = r"(?<!1)3RD"
DECIMAL_ORDINAL_TEENS = r"1[1-9]TH"
DECIMAL_ORDINAL_OTHERWISE = r"(?:(?:10)|(?:(?<!1)[04-9]))TH"
DECIMAL_ORDINAL_PATTERNS = [
    DECIMAL_ORDINAL_ONES,
    DECIMAL_ORDINAL_TWOS,
    DECIMAL_ORDINAL_THREES,
    DECIMAL_ORDINAL_TEENS,
    DECIMAL_ORDINAL_OTHERWISE,
]
DECIMAL_ORDINAL_STRICT_P = re.compile(
    rf"\d*(?:{'|'.join(DECIMAL_ORDINAL_PATTERNS)})",
    re.IGNORECASE,
)


def try_normalize_ordinal(s: str, strict: bool = False) -> typing.Optional[str]:
    """Try to normalize a numeric ordinal.

    Attempts to normalize an ordinal number in numeric (integer) form.
    e.g.:
    1st -> FIRST
    12nd -> TWELVTH
    23rd -> TWENTY-THIRD

    If the input is not an ordinal number or has the wrong suffix (e.g. 1nd, 2th),
    then None is returned.
    """
    if strict:
        if DECIMAL_ORDINAL_STRICT_P.fullmatch(s):
            return int_to_ordinal(int(s[:-2]))
    elif DECIMAL_ORDINAL_NONSTRICT_P.fullmatch(s):
        return int_to_ordinal(int(s[:-2]))


def try_ordinalize(s: str, strict: bool = False) -> typing.Optional[str]:
    """Try to normalize a numeric ordinal, converting cardinals to ordinals."""
    if s.isdecimal():
        return int_to_ordinal(int(s))
    return try_normalize_ordinal(s, strict)


def try_digit_ordinal_to_word(s: str, strict: bool = False) -> typing.Optional[str]:
    """Try to convert digit ordinal to word ordinal.

    For example: "34TH" to "THIRTY-FOURTH".

    If strict is True, digit ordinals with the wrong suffix will not be converted.
    For example, "34ST" is result in None.

    Arguments:
        s: String to conert if a digit ordinal.
        strict: If to only convert digit ordinals with the correct suffix.
    """
    if m := re.fullmatch(r"(\d+)(ST|ND|RD|TH)?", s):
        n = int(m.group(1))
        _suffix: str = m.group(2)

        suffix = _ordinal_suffix(n)
        assert suffix is not None
        res = f"{n}{suffix}"

        if _suffix:
            if strict and suffix != _suffix.upper():
                return None
            if not _suffix.isupper():
                return res.lower()
        return res


def is_digit_ordinal(s: str, strict: bool = False) -> bool:
    """Is string a digit ordinal?

    For example "34TH".
    """
    return try_digit_ordinal_to_word(s, strict) == s.upper()
    # if (n := try_digit_ordinalize(s, strict)) is not None:
    #     return n == s.upper()
    # return False


def digit_ordinalize(s: str, strict: bool = False) -> str:
    """Convert digit ordinals to word ordinals or return original input."""
    if (_s := try_digit_ordinal_to_word(s, strict)) is not None:
        return _s
    return s


class _Number(int):
    def __init__(self, n: int, is_period: bool, is_ordinal: bool):
        self.__period = is_period
        self.__ordinal = is_ordinal

    def __new__(cls, n: int, _is_period: bool, _is_ordinal: bool):
        return super(_Number, cls).__new__(cls, n)

    def __repr__(self) -> str:
        if self.period:
            if self.ordinal:
                return f"PO({int(1000**self)})"
            return f"PC({int(1000**self)})"
        else:
            if self.ordinal:
                return f"O({int(self)})"
            return f"C({int(self)})"

    @property
    def period(self) -> bool:
        return self.__period

    @property
    def ordinal(self) -> bool:
        return self.__ordinal

    @property
    def cardinal(self) -> bool:
        return not self.ordinal


ZERO = {
    "ZERO": _Number(0, False, False),
    "ZEROTH": _Number(0, False, True),
}


HUNDRED = {
    "HUNDRED": _Number(100, False, False),
    "HUNDREDTH": _Number(100, False, True),
}


def _lookup_number(s: str, take_digits: bool) -> typing.Optional[_Number]:
    # NOTE:
    # Disabled while thinking this through...
    # What exactly you allow disallow here is a can or worms.
    # - "2 HUNDRED"
    # - "THREE 1000" ???
    # if take_digits and s.isdecimal():
    #     return _Number(int(s), False, False)
    _s = s.upper()
    ordinal = _s.endswith("TH")
    if (p := PERIOD_TO_INT.get(_s[:-2] if ordinal else _s)) is not None:
        return _Number(p, True, ordinal)
    if (n := ZERO.get(_s)) is not None:
        return n
    if (n := HUNDRED.get(_s)) is not None:
        return n
    if (n := CARDINAL_TO_INT.get(_s)) is not None:
        return _Number(n, False, False)
    if (n := ORDINAL_TO_INT.get(_s)) is not None:
        return _Number(n, False, True)


def _is_number(s: str, take_digits: bool = False) -> bool:
    return _lookup_number(s, take_digits) is not None


WORD_P = re.compile(r"(?:(\S+)-)?(\S+)|AND")


def _is_number_match(
    m: typing.Match[str],
    take_and: bool,
) -> bool:
    w = m.group().upper()
    # NOTE:
    # See _lookup_number notes...
    # if w.isdecimal():
    #     return True
    if take_and and w == "AND":
        return True
    if all(map(_is_number, filter(None, m.groups()))):
        return True
    return False


def _iter_number_spans(
    s: str,
    take_and: bool,
) -> typing.Iterator[typing.Tuple[int, int]]:
    matches: typing.List[typing.Match[str]] = list()
    for m in WORD_P.finditer(s):
        if _is_number_match(m, take_and):
            matches.append(m)
        elif len(matches) > 0:
            span = (matches[0].start(), matches[-1].end())
            yield span
            matches.clear()
    if len(matches) > 0:
        yield (matches[0].start(), matches[-1].end())


def _collect_number_parts(
    s: str,
    take_and: bool,
    take_digits: bool,
) -> typing.Optional[typing.List[_Number]]:
    parts: typing.List[_Number] = list()
    for m in WORD_P.finditer(s):
        for w in filter(None, m.groups()):
            if take_and and w.upper() == "AND":
                continue
            n = _lookup_number(w, take_digits)
            if n is None:
                return None
            parts.append(n)
    if len(parts) > 0:
        return parts


class _PartsKind(enum.Enum):
    CARDINAL = enum.auto()
    ORDINAL = enum.auto()
    CARDINAL_IMPROPER = enum.auto()
    ORDINAL_IMPROPER = enum.auto()

    @property
    def cardinal(self) -> bool:
        return self in (_PartsKind.CARDINAL, _PartsKind.CARDINAL_IMPROPER)

    @property
    def ordinal(self) -> bool:
        return self in (_PartsKind.ORDINAL, _PartsKind.ORDINAL_IMPROPER)

    @property
    def improper(self) -> bool:
        return self in (_PartsKind.CARDINAL_IMPROPER, _PartsKind.ORDINAL_IMPROPER)

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return repr(self)

    def to_improper(self) -> _PartsKind:
        if self in (_PartsKind.CARDINAL, _PartsKind.CARDINAL_IMPROPER):
            return _PartsKind.CARDINAL_IMPROPER
        if self in (_PartsKind.ORDINAL, _PartsKind.ORDINAL_IMPROPER):
            return _PartsKind.ORDINAL_IMPROPER
        raise NotImplementedError

    @staticmethod
    def from_flags(ordinal: bool, improper: bool) -> _PartsKind:
        if not ordinal:
            if not improper:
                return _PartsKind.CARDINAL
            else:
                return _PartsKind.CARDINAL_IMPROPER
        else:
            if not improper:
                return _PartsKind.ORDINAL
            else:
                return _PartsKind.ORDINAL_IMPROPER


def _parse_number_parts(
    parts: typing.List[_Number],
    strict_periods: bool,
    strict_hundreds: bool,
    ordinal_bounds: bool,
) -> typing.Iterator[typing.Tuple[int, _PartsKind]]:
    n: typing.Optional[int] = None
    kind = _PartsKind.CARDINAL
    stack: typing.List[int] = list()
    for part in parts:
        logger.log(0, f"part {part} {stack=}")
        if part.period:
            p = 1000**part
            f = sum(stack)
            stack.clear()
            # NOTE: something is wrong here.
            # need to figure out where handling strict stuff really needs to be
            if f == 0:
                if not strict_periods:
                    kind = kind.to_improper()
            n = (n or 0) + max(1, f) * p
        elif part == 100:
            f = sum(stack)
            if f != 0 or not strict_hundreds:
                stack.clear()
                stack.append(max(1, f) * part)
        else:
            stack.append(part)
            n = n or 0

        if part.ordinal and ordinal_bounds and n is not None:
            yield (n or 0) + sum(stack), _PartsKind.ORDINAL
            n = None
            kind = _PartsKind.CARDINAL
            stack.clear()
        if part.ordinal:
            if kind.ordinal:
                kind = _PartsKind.ORDINAL_IMPROPER
            else:
                kind = _PartsKind.ORDINAL
    if n is not None or len(stack) > 0:
        yield (n or 0) + sum(stack), kind


@dataclass
class DecimalizeParams:
    """Decimalize parameters.

    A few definitions:

    - A *period* is a groups of digits when writing/speaking numbers standard form. In
      English, a period is three digits. But words like "thousand", "million", "billion"
      represent a different power of a thousand.
    - A *simple number* is one with a single or two digits; e.g. 1, 23, 99.

    Fields:
        strict_periods: Periods must start with a simple number or hundred.
        strict_hundreds: Hundreds must start with a simple number.
        take_and: With any "AND" present, only accept if they join periods/hundreds.
        ignore_and: Ignore any "AND" regardless of where.
        take_digits: Allow pure digits.
        ordinal_bounds: Numbers are terminated by ordinal suffixes.
    """

    correct_suffixes: bool = True

    strict_periods: bool = True
    strict_hundreds: bool = True

    # TODO: implement take_and/ignore_and usage
    take_and: bool = True
    ignore_and: bool = False
    # TODO: do something with take_digits
    take_digits: bool = True

    ordinal_bounds: bool = True

    cardinal: bool = True
    cardinal_improper: bool = True
    ordinal: bool = True
    ordinal_improper: bool = True

    def take_kind(self, k: _PartsKind) -> bool:
        """Get paramter flag from parts kind."""
        if k == _PartsKind.CARDINAL:
            return self.cardinal
        elif k == _PartsKind.ORDINAL:
            return self.ordinal
        elif k == _PartsKind.CARDINAL_IMPROPER:
            return self.cardinal_improper
        elif k == _PartsKind.ORDINAL_IMPROPER:
            return self.ordinal_improper
        raise ValueError


def _decimalize_sub(
    s: str,
    params: DecimalizeParams,
) -> typing.Iterator[typing.Tuple[str, typing.Optional[_PartsKind]]]:
    # TODO: figure out what the IndexError was coming from, document as "Raises:"
    # with suppress(IndexError):
    if parts := _collect_number_parts(
        s,
        params.take_and,
        params.take_digits,
    ):
        logger.log(0, parts)
        for n, k in _parse_number_parts(
            parts,
            params.strict_periods,
            params.strict_hundreds,
            params.ordinal_bounds,
        ):
            logger.debug(f"decimalized {n=} {k} take={params.take_kind(k)}")
            if params.take_kind(k):
                t = str(n) if k.cardinal else f"{n}{_ordinal_suffix(n)}"
                yield t, k
            else:
                yield s, None


A = typing.TypeVar("A")
B = typing.TypeVar("B")


def _intersperse(iterable: typing.Iterable[A], fill: B) -> typing.Iterator[A | B]:
    it = iter(iterable)
    with suppress(StopIteration):
        yield next(it)
        for v in it:
            yield fill
            yield v


def decimalize(
    s: str,
    params: DecimalizeParams | None = None,
) -> str:
    """Convert ordinal/cardinal numbers in string input to decimal form."""
    _n = operator.itemgetter(0)

    params = params or DecimalizeParams()
    result_parts: typing.List[str] = list()
    i = 0
    for span_l, span_r in _iter_number_spans(s, params.take_and):
        w = s[span_l:span_r]
        logger.log(0, f"number span {(w, (i, span_l))}")
        if (t := s[i:span_l]) != "":
            result_parts.append(t)
        result_parts.extend(_intersperse(map(_n, _decimalize_sub(w, params)), " "))
        i = span_r
    if (t := s[i:]) != "":
        result_parts.append(t)
    s = "".join(result_parts)
    if not params.correct_suffixes:
        return s
    return " ".join(map(fix_decimal_ordinal, s.split()))
