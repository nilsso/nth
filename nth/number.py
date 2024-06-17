"""Integer to cardinal/ordinal (or vice versa) lookup tables."""

from __future__ import annotations

import logging
import typing

logger = logging.getLogger(__name__)


class Integer(int):
    """Integer helper."""

    ordinal: bool
    word: bool
    period: bool

    def __init__(
        self,
        n: int,
        ordinal: bool = False,
        word: bool = False,
        period: bool = False,
    ):
        """Initialize."""
        del n
        self.ordinal = ordinal
        self.word = word
        self.period = period

    def __new__(
        cls,
        n: int,
        ordinal: bool = False,
        word: bool = False,
        period: bool = False,
    ):
        """Construct."""
        del ordinal, word, period
        return super(Integer, cls).__new__(cls, n)

    def copy(
        self,
        n: int | None = None,
        ordinal: bool | None = None,
        word: bool | None = None,
        period: bool | None = None,
    ) -> Integer:
        """Copy this number (and optionally replace particular fields)."""
        n = n if n is not None else int(self)
        o = ordinal if ordinal is not None else self.ordinal
        w = word if word is not None else self.word
        p = period if period is not None else self.period
        return Integer(n, o, w, p)

    @property
    def hundred(self) -> bool:
        """Is one hundred?"""
        return self == 100

    @property
    def decimal(self) -> bool:
        """Number should be in decimal form."""
        return not self.word

    @property
    def cardinal(self) -> bool:
        """Number should be of cardinal kind (i.e. a counting number)."""
        return not self.ordinal

    def __repr__(self) -> str:
        """Convert to programmer-facing, debugging context, string."""
        k = "O" if self.ordinal else "C"
        f = "W" if self.word else ""
        p = "P" if self.period else ""
        n = f"1000^{int(self)}" if self.period else int(self)
        return f"{k}{f}{p}({n})"

    def __str__(self) -> str:
        """Convert to interger string.

        Note: See {nth.format_number} for formatting according to {nth.FormatArg}.
        """
        return str(int(self))

    def __iter__(self):
        """Field iterator."""
        yield int(self)
        yield self.ordinal
        yield self.period

    def __hash__(self):
        """Hash."""
        return hash(tuple(self))

    def __eq__(self, other: typing.Any) -> bool:
        """Equality.

        If other is a {Number} equality is strict on all fields; if other is an integer
        then equality is simple integer equality; and is False for any other type.
        """
        match other:
            case int():
                return int(self) == other
            case Integer():
                return tuple(self) == tuple(other)
            case _:
                return False

    @staticmethod
    def _op_validate(other: typing.Any):
        if isinstance(other, Integer):
            return not other.period
        return isinstance(other, int)

    def __add__(self, other: Integer | int) -> Integer:
        """Addition operator."""
        if self.period:
            raise ValueError(f"cannot add lhs={self}")
        if not Integer._op_validate(other):
            raise ValueError(f"cannot add rhs={self}")
        n = int(self) + int(other)
        o = self.ordinal or isinstance(other, Integer) and other.ordinal
        # TODO: what to do if differed __word?
        return Integer(n, o, self.word)

    def __radd__(self, other: Integer | int) -> Integer:
        """Reversed addition operator."""
        return self + other
