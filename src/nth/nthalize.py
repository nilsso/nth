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
import re
import typing

from ._utils import intersperse
from .number import Integer
from .words import lookup_word, try_lookup_number

logger = logging.getLogger(__name__)


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
        match d:
            case 1:
                return Suffix.ST
            case 2:
                return Suffix.ND
            case 3:
                return Suffix.RD
            case _:
                return Suffix.TH


def int_to_decimal_ordinal(n: int) -> str:
    """Convert integer to decimal ordinal string."""
    suffix = Suffix.for_int(n)
    return f"{n}{suffix.value}"


# Match a decimal ordinal (non-strict).
DECIMAL_ORDINAL_NONSTRICT_P = re.compile(
    r"\b(\d+)(ST|ND|RD|TH)\b",
    re.IGNORECASE,
)


def is_ordinal_decimal(s: str, strict: bool = False) -> bool:
    """Is string a decimal ordinal number."""
    if m := DECIMAL_ORDINAL_NONSTRICT_P.fullmatch(s):
        if not strict:
            return True
        return s.upper() == int_to_decimal_ordinal(int(m.group(1)))
    return False


def is_decimal(s: str, strict: bool = False) -> bool:
    """Is string a decimal number.

    Differs from the usual {str.isdecimal} by accepting ordinal numbers as well.
    """
    return s.isdecimal() or is_ordinal_decimal(s, strict)


def is_cardinal_decimal(s: str, strict: bool = False) -> bool:
    """Is string a decimal cardinal number."""
    return s.isdecimal() and not is_ordinal_decimal(s, strict)


def contains_ordinal_decimal(s: str, strict: bool = False) -> bool:
    for m in DECIMAL_ORDINAL_NONSTRICT_P.finditer(s):
        if not strict:
            return True
        if s.upper() == int_to_decimal_ordinal(int(m.group(1))):
            return True
    return False


def try_decimal_to_int(s: str, strict: bool = False) -> int | None:
    """Convert string to integer if it represents a decimal number."""
    if is_decimal(s, strict):
        if is_ordinal_decimal(s):
            return int(s[:-2])
        return int(s)


def decimal_to_int(s: str, strict: bool = False) -> int:
    """Convert string to integer."""
    n = try_decimal_to_int(s, strict)
    assert n is not None
    return n


def is_number_word(s: str) -> bool:
    """Is string a number word?"""
    return try_lookup_number(s) is not None


class Span(typing.NamedTuple):
    """Span tuple helper."""

    left: int
    right: int

    def to_slice(self) -> slice:
        """To slice object."""
        return slice(*self)

    def slice(self, s: str) -> str:
        """Slice a string."""
        return s[self.to_slice()]


def is_number_word_match(m: typing.Match[str]) -> bool:
    """Is Match object over a number word?"""
    return all(map(is_number_word, filter(None, m.groups())))


# Roughly match cardinal/ordinal words.
NUMBERISH_WORD_P = re.compile(
    r"\b(?:(?:([^\s,.]+)-)?([^\s,.]+))\b",
    re.IGNORECASE,
)


def iter_number_spans(s: str) -> typing.Iterator[Span]:
    """Iterate substring spans that are numeric."""
    matches: list[typing.Match[str]] = list()

    def full_span() -> Span | None:
        if len(matches) > 0:
            span = Span(matches[0].start(), matches[-1].end())
            matches.clear()
            return span

    for m in NUMBERISH_WORD_P.finditer(s):
        n = m.group()
        logger.log(1, f"number-ish word {n=} groups={m.groups()} {len(matches)=}")
        if n == ",":
            if span := full_span():
                yield span
        elif is_decimal(n):
            if span := full_span():
                yield span
            yield Span(*m.span())
        elif n.upper() == "AND":
            continue
        elif is_number_word_match(m):
            matches.append(m)
        elif span := full_span():
            yield span
    if span := full_span():
        yield span


def contains_numbers(s: str) -> bool:
    """Does string contain any number-like sequences?"""
    del s
    raise NotImplementedError
    # try:
    #     next(iter_number_spans(s))
    #     return True
    # except StopIteration:
    #     return False


def try_parse_word_number(
    s: str,
    word_behavior: WordBehavior,
) -> typing.Iterator[Integer | str]:
    """Try to parse as multi-word number."""
    # TODO: use word_behavior
    del word_behavior
    n: Integer | None = None
    stack: list[Integer] = []

    def try_take():
        if n is not None or len(stack) > 0:
            res = (n or Integer(0)) + sum(stack)
            return res

    for w in s.upper().replace("-", " ").split():
        if w == "AND":
            continue
        else:
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
                f = max(1, sum(stack))
                stack.clear()
                if p.period:
                    v = f * 1000**p
                    n = (n or Integer(0)) + v
                else:  # hundred
                    v = f * p
                    stack.append(Integer(v))
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


def try_parse_numbers(
    s: str,
    word_behavior: WordBehavior,
) -> typing.Iterator[Integer | str]:
    """Try to parse string as number of either decimal or word format."""
    if (n := try_decimal_to_int(s)) is not None:
        yield Integer(n, ordinal=is_ordinal_decimal(s))
    else:
        for v in try_parse_word_number(s, word_behavior):
            yield v


def number_to_word_parts(n: Integer) -> list[Integer]:
    """Construct {Number} parts for conversion to a word format."""
    _n = n.copy()
    if _n == 0:
        return [_n]

    parts: list[Integer] = []
    e = 0
    while _n > 0:
        p = _n % 1000
        if p > 0 and e > 0:
            a = Integer(e, period=True)
            parts.append(a)
        h, r = divmod(p, 100)
        if 10 < r < 20:
            parts.append(Integer(r))
        else:
            t, o = divmod(r, 10)
            if o > 0:
                parts.append(Integer(o))
            if t > 0:
                parts.append(Integer(10 * t))
            if h > 0:
                parts.append(Integer(100))
                parts.append(Integer(h))
        _n //= 1000
        e += 1
    return list(reversed(parts))


def number_to_decimal_str(n: Integer, as_ordinal: bool = False) -> str:
    """Convert number to decimal format string."""
    if as_ordinal:
        return int_to_decimal_ordinal(n)
    return str(int(n))


def number_to_word_str(n: Integer, as_ordinal: bool = False) -> str:
    """Convert number to word format string."""
    parts = number_to_word_parts(n)
    if as_ordinal:
        parts[-1].ordinal = True
        # NOTE: should all periods be ordinal?
        # for p in parts:
        #     if p.period:
        #         p.ordinal = True
    return " ".join(map(lookup_word, parts))


def format_number(
    n: Integer,
    as_ordinal: bool = False,
    as_words: bool = False,
) -> str:
    """Convert to specified format."""
    res: str | None = None
    if as_words:
        res = number_to_word_str(n, as_ordinal)
    else:
        res = number_to_decimal_str(n, as_ordinal)
    logger.debug(f"formatted {n=} -> {res=}")
    assert res is not None
    return res


# class DecimalBehavior(typing.TypedDict):
#     """Decimal behavior argument pack."""
#     pass


WordAndBehavior: typing.TypeAlias = typing.Literal["IGNORE", "STRICT", "DENY"]


class WordBehavior(typing.TypedDict):
    """Word behavior argument pack."""

    and_behavior: WordAndBehavior


def default_word_behavior() -> WordBehavior:
    """Make default word behavior argument pack."""
    return WordBehavior(
        and_behavior="IGNORE",
    )


NumberKind: typing.TypeAlias = typing.Literal["CARDINAL", "ORDINAL"]
FormatKind: typing.TypeAlias = typing.Literal["DECIMAL", "WORD"]


class NthalizeArgs(typing.TypedDict):
    """Nthalize argument pack."""

    number: NumberKind | None
    format: FormatKind | None
    # decimal_behavior: DecimalBehavior
    word_behavior: WordBehavior | None


def default_args() -> NthalizeArgs:
    """Make default nthalize argument pack."""
    return NthalizeArgs(
        number="CARDINAL",
        format="DECIMAL",
        word_behavior=default_word_behavior(),
    )


class _NthalizeArgs(typing.NamedTuple):
    as_ordinal: bool
    as_word: bool
    word_behavior: WordBehavior

    @staticmethod
    def default() -> _NthalizeArgs:
        return _NthalizeArgs.new(default_args())

    @staticmethod
    def new(args: NthalizeArgs | None) -> _NthalizeArgs:
        if args is None:
            return _NthalizeArgs.default()
        match args.get("number"):
            case "CARDINAL" | None:
                as_ordinal = False
            case "ORDINAL":
                as_ordinal = True
            case unreachable:  # pyright: ignore[reportUnnecessaryComparison]
                raise ValueError(unreachable)
        match args.get("format"):
            case "DECIMAL" | None:
                as_word = False
            case "WORD":
                as_word = True
            case unreachable:  # pyright: ignore[reportUnnecessaryComparison]
                raise ValueError(unreachable)
        word_behavior = args.get("word_behavior") or default_word_behavior()
        return _NthalizeArgs(
            as_ordinal,
            as_word,
            word_behavior,
        )


def nthalize(s: str, args: NthalizeArgs | None = None):
    """Nthalize throughout a string."""
    _args = _NthalizeArgs.new(args)

    def map_n(n: Integer) -> str:
        return format_number(n, _args.as_ordinal, _args.as_word)

    def map_nw(n: Integer | str) -> str:
        match n:
            case str():
                res = n
            case Integer():
                res = map_n(n)
        logger.log(5, f"{n=} -> {res=}")
        return res

    i = 0
    res: list[str] = []
    for span in iter_number_spans(s):
        if (w := s[i : span.left]) != "":
            res.append(w)
        w = span.slice(s)
        logger.debug(f'number span "{w}" {tuple(span)}')
        n_it = try_parse_numbers(w, _args.word_behavior)
        a = intersperse(n_it, " ")
        b = map(map_nw, a)
        res.extend(b)
        # res.extend(map(map_nw, intersperse(n_it, " ")))
        i = span.right
    if (w := s[i:]) != "":
        res.append(w)
    return "".join(res)
