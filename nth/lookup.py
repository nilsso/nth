"""String to number lookup."""

from __future__ import annotations

from typing import Iterable

from .number import Integer

# TODO:
# consider mixing in "corrections". e.g.:
# - "TWELVTH, "TWELVETH
# - "FORTHEENTH


def try_lookup_number(w: str) -> Integer | None:
    """Lookup {Number} from number word or None if not found.

    Only accepts single word numbers, like "1" or "TWENTY", and not "TWENTY ONE".
    For multiword use the full {try_parse} algorithm.
    """
    _w = w.upper()
    for d in N_LOOKUPS:
        if (n := d.get(_w)) is not None:
            return n


def lookup_number(w: str) -> Integer:
    """Lookup {Number} from number word."""
    n = try_lookup_number(w)
    if n is None:
        raise ValueError(f"lookup_number {w=}")
    return n


def try_lookup_word(n: Integer) -> str | None:
    """Lookup number word from {Number} or None if not found."""
    for d in WORD_LOOKUPS:
        if (w := d.get(n)) is not None:
            return w


def lookup_word(n: Integer) -> str:
    """Lookup number word from {Number}."""
    w = try_lookup_word(n)
    if w is None:
        raise ValueError(f"lookup_word {w=}")
    return w


type ParamNoAliases = tuple[int, str]
type ParamWithAliases = tuple[int, str, set[str]]

type Param = ParamNoAliases | ParamWithAliases


def make_lookups(
    *,
    ordinal: bool,
    period: bool,
    params: Iterable[Param],
) -> tuple[dict[Integer, str], dict[str, Integer]]:
    n_to_t = dict[Integer, str]()
    t_to_n = dict[str, Integer]()
    for p in params:
        match p:
            case (n, t):
                aliases = None
            case (n, t, aliases):
                ...
        n = Integer(n, ordinal=ordinal, word=False, period=period)
        w = Integer(n, ordinal=ordinal, word=True, period=period)
        n_to_t[n] = t
        t_to_n[t] = w
        if aliases:
            for t in aliases:
                t_to_n[t] = w
    return n_to_t, t_to_n


N_TO_CARDINAL, CARDINAL_TO_N = make_lookups(
    ordinal=False,
    period=False,
    params=[
        (1, "ONE"),
        (2, "TWO"),
        (3, "THREE"),
        (4, "FOUR"),
        (5, "FIVE"),
        (6, "SIX"),
        (7, "SEVEN"),
        (8, "EIGHT"),
        (9, "NINE"),
        (10, "TEN"),
        (11, "ELEVEN"),
        (12, "TWELVE"),
        (13, "THIRTEEN"),
        (14, "FOURTEEN"),
        (15, "FIFTEEN"),
        (16, "SIXTEEN"),
        (17, "SEVENTEEN"),
        (18, "EIGHTEEN"),
        (19, "NINETEEN"),
        (20, "TWENTY"),
        (30, "THIRTY"),
        (
            40,
            "FORTY",
            {"FOURTY"},
        ),
        (50, "FIFTY"),
        (60, "SIXTY"),
        (70, "SEVENTY"),
        (80, "EIGHTY"),
        (90, "NINETY"),
        (100, "HUNDRED"),
    ],
)

N_TO_ORDINAL, ORDINAL_TO_N = make_lookups(
    ordinal=True,
    period=False,
    params=[
        (0, "ZERO"),
        (1, "FIRST"),
        (2, "SECOND"),
        (3, "THIRD"),
        (4, "FOURTH"),
        (5, "FIFTH"),
        (6, "SIXTH"),
        (7, "SEVENTH"),
        (8, "EIGHTH"),
        (9, "NINTH"),
        (10, "TENTH"),
        (11, "ELEVENTH"),
        (
            12,
            "TWELFTH",
            {"TWELVTH"},
        ),
        (13, "THIRTEENTH"),
        (
            14,
            "FOURTEENTH",
            {"FORTEENTH", "FOURTHEENTH", "FORTHEENTH"},
        ),
        (15, "FIFTEENTH"),
        (16, "SIXTEENTH"),
        (17, "SEVENTEENTH"),
        (18, "EIGHTEENTH"),
        (19, "NINETEENTH"),
        (20, "TWENTIETH"),
        (30, "THIRTIETH"),
        (
            40,
            "FORTIETH",
            {"FOURTIETH"},
        ),
        (50, "FIFTIETH"),
        (60, "SIXTIETH"),
        (70, "SEVENTIETH"),
        (80, "EIGHTIETH"),
        (90, "NINETIETH"),
        (100, "HUNDREDTH"),
    ],
)

N_TO_CARDINAL_PERIOD, CARDINAL_PERIOD_TO_N = make_lookups(
    ordinal=False,
    period=True,
    params=[
        (0, "ZEROTH"),
        (1, "THOUSAND"),
        (2, "MILLION"),
        (3, "BILLION"),
        (4, "TRILLION"),
        (5, "QUADRILLION"),
        (6, "QUINTILLION"),
    ],
)

N_TO_ORDINAL_PERIOD, ORDINAL_PERIOD_TO_N = make_lookups(
    ordinal=True,
    period=True,
    params=[
        (1, "THOUSANDTH"),
        (2, "MILLIONTH"),
        (3, "BILLIONTH"),
        (4, "TRILLIONTH"),
        (5, "QUADRILLIONTH"),
        (6, "QUINTILLIONTH"),
    ],
)

N_LOOKUPS = [
    CARDINAL_TO_N,
    ORDINAL_TO_N,
    CARDINAL_PERIOD_TO_N,
    ORDINAL_PERIOD_TO_N,
]

WORD_LOOKUPS = [
    N_TO_CARDINAL,
    N_TO_ORDINAL,
    N_TO_CARDINAL_PERIOD,
    N_TO_ORDINAL_PERIOD,
]
