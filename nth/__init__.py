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
import logging
import os
import re
import typing
from contextlib import suppress
from dataclasses import dataclass

from .lookup import try_lookup_number, try_lookup_word
from .number import Number

logger = logging.getLogger(__name__)
if (log_level_str := os.environ.get("NTH_LEVEL")) is not None:
    if log_level_str.isdecimal():
        log_level = int(log_level_str)
    else:
        log_level = logging.getLevelName(log_level_str)
    logger.setLevel(log_level)


_T1 = typing.TypeVar("_T1")
_T2 = typing.TypeVar("_T2")


def intersperse(
    iterable: typing.Iterable[_T1],
    fill: _T2,
) -> typing.Iterator[_T1 | _T2]:
    """Intersperse."""
    it = iter(iterable)
    with suppress(StopIteration):
        yield next(it)
        for v in it:
            yield fill
            yield v


class FormatArg(enum.Enum):
    """Format argument type."""

    CARDINAL_DECIMAL = enum.auto()
    CARDINAL_WORD = enum.auto()
    ORDINAL_DECIMAL = enum.auto()
    ORDINAL_WORD = enum.auto()

    @property
    def cardinal(self) -> bool:
        """Is this a cardinal format?"""
        return cardinal_format(self)

    @property
    def ordinal(self) -> bool:
        """Is this an ordinal format?"""
        return not self.cardinal

    @property
    def decimal(self) -> bool:
        """Is this a decimal format?"""
        return decimal_format(self)

    @property
    def word(self) -> bool:
        """Is this a word format?"""
        return not self.decimal


_Enum = typing.TypeVar("_Enum", bound=enum.Enum)
_VariantGuard: typing.TypeAlias = typing.TypeGuard[_Enum]

_CardinalFormat: typing.TypeAlias = typing.Literal[
    FormatArg.CARDINAL_DECIMAL,
    FormatArg.CARDINAL_WORD,
]
_OrdinalFormat: typing.TypeAlias = typing.Literal[
    FormatArg.ORDINAL_DECIMAL,
    FormatArg.ORDINAL_WORD,
]
_DecimalFormat: typing.TypeAlias = typing.Literal[
    FormatArg.CARDINAL_DECIMAL,
    FormatArg.ORDINAL_DECIMAL,
]
_WordFormat: typing.TypeAlias = typing.Literal[
    FormatArg.CARDINAL_WORD,
    FormatArg.ORDINAL_WORD,
]


def cardinal_format(fmt: FormatArg) -> _VariantGuard[_CardinalFormat]:
    """Type guard format is a cardinal variant."""
    return fmt in (FormatArg.CARDINAL_DECIMAL, FormatArg.CARDINAL_WORD)


def ordinal_format(fmt: FormatArg) -> _VariantGuard[_OrdinalFormat]:
    """Type guard format is an ordinal variant."""
    return not cardinal_format(fmt)


def decimal_format(fmt: FormatArg) -> _VariantGuard[_DecimalFormat]:
    """Type guard format is a decimal format."""
    return fmt in (FormatArg.CARDINAL_DECIMAL, FormatArg.ORDINAL_DECIMAL)


def word_format(fmt: FormatArg) -> _VariantGuard[_WordFormat]:
    """Type guard format is a word format."""
    return not decimal_format(fmt)


class CardinalAndArg(enum.Enum):
    """Cardinal "and" behavior."""

    IGNORE = enum.auto()
    STRICT = enum.auto()
    DENY = enum.auto()


@dataclass
class CardinalArgs:
    """Cardinal behavior argument pack."""

    and_behavior: CardinalAndArg


@dataclass
class NthalizeArgs:
    """Nthalize argument pack."""

    format: FormatArg
    cardinal_and: CardinalAndArg = CardinalAndArg.IGNORE


class Suffix(str, enum.Enum):
    """Ordinal suffix."""

    ST = "ST"
    ND = "ND"
    RD = "RD"
    TH = "TH"

    @staticmethod
    def for_int(n: int) -> Suffix:
        """Get suffix for integer."""
        if 10 < (n % 100) < 20:
            return Suffix.TH
        d = n % 10
        if d == 1:
            return Suffix.ST
        elif d == 2:
            return Suffix.ND
        elif d == 3:
            return Suffix.RD
        else:
            return Suffix.TH


def int_to_decimal_ordinal(n: int) -> str:
    """Convert integer to decimal ordinal string."""
    return f"{n}{Suffix.for_int(n)}"


# Roughly match cardinal/ordinal words.
NUMBERISH_WORD_P = re.compile(
    r"(?:(\S+)-)?(\S+)|AND",
    re.IGNORECASE,
)

# Match a decimal ordinal (non-strict).
DECIMAL_ORDINAL_NONSTRICT_P = re.compile(
    r"\b(\d+)(ST|ND|RD|TH)\b",
    re.IGNORECASE,
)


def is_ordinal_number(s: str, strict: bool = False) -> bool:
    """Is string an ordinal number (decimal or word form)."""
    if m := DECIMAL_ORDINAL_NONSTRICT_P.fullmatch(s):
        if not strict:
            return True
        return s.upper() == int_to_decimal_ordinal(int(m.group(1)))
    return False


def is_number(s: str, strict: bool = False) -> bool:
    """Is string a number (cardinal or ordinal, decimal or word form)."""
    return s.isdecimal() or is_ordinal_number(s, strict)


def is_cardinal_number(s: str, strict: bool = False) -> bool:
    """Is string a cardinal number (decimal or word form)."""
    return s.isdecimal() and not is_ordinal_number(s, strict)


def is_number_word(s: str) -> bool:
    """Is string a number word?"""
    return try_lookup_number(s) is not None


def is_number_word_match(m: typing.Match[str]) -> bool:
    """Is Match object over a number word?"""
    return all(map(is_number_word, filter(None, m.groups())))


class Span(typing.NamedTuple):
    """Span tuple helper."""

    l: int
    r: int

    def to_slice(self) -> slice:
        """To slice object."""
        return slice(*self)

    def slice(self, s: str) -> str:
        """Slice a string."""
        return s[self.to_slice()]


def iter_number_spans(s: str) -> typing.Iterator[Span]:
    """Iterate substring spans that are numeric."""
    matches: list[typing.Match[str]] = list()

    def full_span() -> Span | None:
        if len(matches) > 0:
            span = Span(matches[0].start(), matches[-1].end())
            matches.clear()
            return span

    for m in NUMBERISH_WORD_P.finditer(s):
        logger.log(0, m)
        w = m.group()
        if is_number(w):
            if span := full_span():
                yield span
            yield Span(*m.span())
        elif w == "AND":
            continue
        elif is_number_word_match(m):
            matches.append(m)
        elif span := full_span():
            yield span
    if span := full_span():
        yield span


def try_parse_numbers(
    s: str,
    cardinal_and: CardinalAndArg,
) -> typing.Iterator[Number | str]:
    """Try to parse whole string as number."""
    # TODO:
    # - cardinal_and args
    # - ordinal bounds
    del cardinal_and

    n: Number | None = None
    stack: list[Number] = []

    def try_take():
        if n is not None or len(stack) > 0:
            res = (n or Number(0)) + sum(stack)
            return res

    for w in s.upper().replace("-", " ").split():
        if w == "AND":
            continue
        p = try_lookup_number(w)
        logger.log(5, f"part {w=} -> {p=} ({n=} {stack=})")
        if p is None:
            if (v := try_take()) is not None:
                n = None
                stack.clear()
                yield v
            yield w
            continue
        if p.period or p.hundred:
            f = max(Number(1), sum(stack))
            stack.clear()
            if p.period:
                v = f * 1000**p
                n = (n or Number(0)) + v
            else:  # hundred
                v = f * p
                stack.append(Number(v))
        else:
            stack.append(p)

        if p.ordinal:
            if (v := try_take()) is not None:
                n = None
                stack.clear()
                yield v
    if (v := try_take()) is not None:
        n = None
        stack.clear()
        yield v


def number_to_word_parts(n: Number) -> list[Number]:
    """Construct {Number} parts for conversion to a word format."""
    _n = n.copy()
    if _n == 0:
        return [_n]

    parts: list[Number] = []
    e = 0
    while _n > 0:
        p = _n % 1000
        if p > 0 and e > 0:
            parts.append(Number(e, period=True))
        q, r = divmod(p, 100)
        if r > 0:
            parts.append(Number(r))
        if q > 0:
            parts.append(Number(100))
            parts.append(Number(q))
        _n //= 1000
        if _n > 0:
            parts.append(Number(e, False, True))
        e += 1
    return parts


def number_to_decimal_str(n: Number, fmt: _DecimalFormat) -> str:
    """Convert number to decimal format string."""
    raise NotImplementedError


def number_to_word_str(n: Number, fmt: _WordFormat) -> str:
    """Convert number to word format string."""
    parts = number_to_word_parts(n)
    for p in parts:
        w = try_lookup_word(p)
        print(f"{p=}, {w=}")
    return str(n)


def format_number(n: Number, fmt: FormatArg) -> str:
    """Convert to specified format."""
    logger.log(5, f"format {n=}")
    if decimal_format(fmt):
        number_to_decimal_str(n, fmt)
    if word_format(fmt):
        number_to_word_str(n, fmt)
    return str(n)


# class _PartsKind(enum.Enum):
#     CARDINAL = enum.auto()
#     ORDINAL = enum.auto()
#     CARDINAL_IMPROPER = enum.auto()
#     ORDINAL_IMPROPER = enum.auto()
#
#     @property
#     def cardinal(self) -> bool:
#         return self in (_PartsKind.CARDINAL, _PartsKind.CARDINAL_IMPROPER)
#
#     @property
#     def ordinal(self) -> bool:
#         return self in (_PartsKind.ORDINAL, _PartsKind.ORDINAL_IMPROPER)
#
#     @property
#     def improper(self) -> bool:
#         return self in (_PartsKind.CARDINAL_IMPROPER, _PartsKind.ORDINAL_IMPROPER)
#
#     def __repr__(self) -> str:
#         return self.name
#
#     def __str__(self) -> str:
#         return repr(self)
#
#     def to_improper(self) -> _PartsKind:
#         if self in (_PartsKind.CARDINAL, _PartsKind.CARDINAL_IMPROPER):
#             return _PartsKind.CARDINAL_IMPROPER
#         if self in (_PartsKind.ORDINAL, _PartsKind.ORDINAL_IMPROPER):
#             return _PartsKind.ORDINAL_IMPROPER
#         raise NotImplementedError
#
#     @staticmethod
#     def from_flags(ordinal: bool, improper: bool) -> _PartsKind:
#         if not ordinal:
#             if not improper:
#                 return _PartsKind.CARDINAL
#             else:
#                 return _PartsKind.CARDINAL_IMPROPER
#         else:
#             if not improper:
#                 return _PartsKind.ORDINAL
#             else:
#                 return _PartsKind.ORDINAL_IMPROPER


# def _parse_word_number_parts(
#     parts: list[_Number],
#     strict_periods: bool,
#     strict_hundreds: bool,
#     ordinal_bounds: bool,
# ) -> typing.Iterator[tuple[int, _PartsKind]]:
#     n: typing.Optional[int] = None
#     kind = _PartsKind.CARDINAL
#     stack: list[int] = list()
#     for part in parts:
#         logger.log(5, f"part {part} {stack=}")
#         if part.period:
#             p = 1000**part
#             f = sum(stack)
#             stack.clear()
#             # NOTE: something is wrong here.
#             # need to figure out where handling strict stuff really needs to be
#             if f == 0:
#                 if not strict_periods:
#                     kind = kind.to_improper()
#             n = (n or 0) + max(1, f) * p
#         elif part == 100:
#             f = sum(stack)
#             if f != 0 or not strict_hundreds:
#                 stack.clear()
#                 stack.append(max(1, f) * part)
#         else:
#             stack.append(part)
#             n = n or 0
#
#         if part.ordinal and ordinal_bounds and n is not None:
#             yield (n or 0) + sum(stack), _PartsKind.ORDINAL
#             n = None
#             kind = _PartsKind.CARDINAL
#             stack.clear()
#         if part.ordinal:
#             if kind.ordinal:
#                 kind = _PartsKind.ORDINAL_IMPROPER
#             else:
#                 kind = _PartsKind.ORDINAL
#     if n is not None or len(stack) > 0:
#         yield (n or 0) + sum(stack), kind


def nthalize(s: str, args: NthalizeArgs):
    """Nthalize throughout a string."""
    # _n = operator.itemgetter(0)

    i = 0
    res: list[str] = []
    for span in iter_number_spans(s):
        if (w := s[i : span.l]) != "":
            res.append(w)
        w = span.slice(s)
        logger.debug(f'number span "{w}" {tuple(span)}')

        def map_n(n: Number | str) -> str:
            match n:
                case str():
                    res = n
                case Number():
                    res = format_number(n, args.format)
            logger.log(5, f"{n=} -> {res=}")
            return res

        n_it = try_parse_numbers(w, args.cardinal_and)

        res.extend(map(map_n, intersperse(n_it, " ")))
        i = span.r
    if (w := s[i:]) != "":
        res.append(w)
    return "".join(res)
