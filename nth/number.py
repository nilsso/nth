"""Integer to cardinal/ordinal (or vice versa) lookup tables."""
from __future__ import annotations

import logging
import typing

logger = logging.getLogger(__name__)


class Number:
    """Number abstraction."""

    _n: int
    _ordinal: bool
    _word: bool
    _period: bool

    def __init__(
        self,
        n: int,
        ordinal: bool = False,
        word: bool = False,
        period: bool = False,
    ):
        """Initialize."""
        self._n = n
        self._ordinal = ordinal
        self._word = word
        self._period = period

    def copy(
        self,
        n: typing.Optional[int] = None,
        ordinal: typing.Optional[bool] = None,
        word: typing.Optional[bool] = None,
        period: typing.Optional[bool] = None,
    ) -> Number:
        """Copy this number (and optionally replace particular fields)."""
        n = n if n is not None else self._n
        o = ordinal if ordinal is not None else self._ordinal
        w = word if word is not None else self._word
        p = period if period is not None else self._period
        return Number(n, o, w, p)

    @property
    def period(self) -> bool:
        """Number represents a period group (value is exponent of one-thousand)."""
        return self._period

    @property
    def hundred(self) -> bool:
        """Is one hundred?"""
        return self._n == 100

    @property
    def decimal(self) -> bool:
        """Number should be in decimal form."""
        return not self._word

    @property
    def word(self) -> bool:
        """Number should be in word form."""
        return self._word

    @property
    def cardinal(self) -> bool:
        """Number should be of cardinal kind (i.e. a counting number)."""
        return not self._ordinal

    @property
    def ordinal(self) -> bool:
        """Number should be of ordinal kind (i.e. an ordering number)."""
        return self._ordinal

    def __repr__(self) -> str:
        """Convert to programmer-facing, debugging context, string."""
        k = "O" if self.ordinal else "C"
        f = "W" if self.word else ""
        p = "P" if self.period else ""
        n = f"1000^{self._n}" if self._period else self._n
        return f"{k}{f}{p}({n})"

    def __str__(self) -> str:
        """Convert to interger string.

        Note: See {nth.format_number} for formatting according to {nth.FormatArg}.
        """
        return str(self._n)

    @staticmethod
    def _op_validate(other: typing.Any):
        if isinstance(other, Number):
            return not other.period
        return isinstance(other, int)

    def __add__(self, other: Number | int) -> Number:
        """Addition operator."""
        if self.period:
            raise ValueError(f"cannot add lhs={self}")
        if not Number._op_validate(other):
            raise ValueError(f"cannot add rhs={self}")
        n = self._n + other._n if isinstance(other, Number) else other
        o = self.ordinal or isinstance(other, Number) and other.ordinal
        # TODO: what to do if differed __word?
        return Number(n, o, self.word)

    def __radd__(self, other: Number | int) -> Number:
        """Reversed addition operator."""
        return self + other

    # def _validate_args(self, other: object) -> typing.TypeGuard[Number | int]:
    #     match other:
    #         case int() | Number():
    #             return True
    #         case _:
    #             return False
    #
    # def _decompose_args(self, other: Number | int) -> tuple[int, int]:
    #     a: int
    #     b: int
    #     if isinstance(other, int):
    #         match self:
    #             case Number(period=False):
    #                 a, b = self._n, other
    #             case Number(period=True):
    #                 a, b = (1000**self._n), other
    #             case _:
    #                 raise SystemError
    #     else:
    #         match self, other:
    #             case Number(period=False), Number(period=True):
    #                 a, b = self._n, (1000**other._n)
    #             case Number(period=True), Number(period=False):
    #                 a, b = (1000**self._n), other._n
    #             case Number(period=_), Number(period=_):
    #                 a, b = self._n, other._n
    #             case _:
    #                 raise SystemError
    #     return a, b
    #
    # def _arithmetic(
    #     self,
    #     other: object,
    #     f: typing.Callable[[int, int], int],
    # ) -> Number:
    #     if self._validate_args(other):
    #         a, b = self._decompose_args(other)
    #         n = f(a, b)
    #         if isinstance(other, int):
    #             return self.copy(n=n)
    #         o = self.ordinal or other.ordinal
    #         w = self.word or other.word
    #         # p =
    #         # return Number(
    #         #
    #         # )
    #     raise ValueError
    #
    # def _compare(
    #     self,
    #     other: object,
    #     f: typing.Callable[[int, int], bool],
    # ) -> bool:
    #     a, b = self._decompose_args(other)
    #     return f(a, b)
    #
    # def __eq__(self, other: object) -> bool:
    #     """Equal."""
    #     return self._compare(other, int.__eq__)
    #
    # def __ne__(self, other: object) -> bool:
    #     """Not equal."""
    #     return not self == other
    #
    # def __lt__(self, other: object) -> bool:
    #     """Less than."""
    #     return self._compare(other, int.__lt__)
    #
    # def __le__(self, other: object) -> bool:
    #     """Less-than or equal."""
    #     return self < other or self == other
    #
    # def __ge__(self, other: object) -> bool:
    #     """Greater-than or equal to."""
    #     return not self < other
    #
    # def __gt__(self, other: object) -> bool:
    #     """Greater than."""
    #     return not self <= other
