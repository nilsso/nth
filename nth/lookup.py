"""String to number lookup."""
import typing

from .number import Number

# TODO:
# consider mixing in "corrections". e.g.:
# - "TWELVTH, "TWELVETH
# - "FORTHEENTH


def try_lookup_number(s: str) -> typing.Optional[Number]:
    """Lookup {Number} from number word.

    Only accepts single word numbers, like "1" or "TWENTY", and not "TWENTY ONE".
    For multiword use the full {try_parse} algorithm.
    """
    _s = s.upper()
    for d in N_LOOKUPS:
        if (n := d.get(_s)) is not None:
            return n


def try_lookup_word(n: Number) -> typing.Optional[str]:
    """Lookup number word from {Number}."""
    for d in WORD_LOOKUPS:
        if (w := d.get(n)) is not None:
            return w


def _reverse_mapping(d: typing.Dict[Number, str]) -> typing.Dict[str, Number]:
    """Construct reverse map from str to word Number."""
    return {s: n.copy(word=True) for n, s in d.items()}


def _make_map_raw(period: bool):
    def _map_raw(p: typing.Tuple[int, str, str]):
        n, c, o = p
        _c = (Number(n, ordinal=False, word=False, period=period), c)
        _o = (Number(n, ordinal=True, word=False, period=period), o)
        return (_c, _o)

    return _map_raw


def _map_period_raw(p: typing.Tuple[int, str]):
    n, c = p
    return (n, c, c + "TH")


_PARTS_RAW = [
    (1, "ONE", "FIRST"),
    (2, "TWO", "SECOND"),
    (3, "THREE", "THIRD"),
    (4, "FOUR", "FOURTH"),
    (5, "FIVE", "FIFTH"),
    (6, "SIX", "SIXTH"),
    (7, "SEVEN", "SEVENTH"),
    (8, "EIGHT", "EIGHTH"),
    (9, "NINE", "NINTH"),
    (10, "TEN", "TENTH"),
    (11, "ELEVEN", "ELEVENTH"),
    (12, "TWELVE", "TWELFTH"),
    (13, "THIRTEEN", "THIRTEENTH"),
    (14, "FOURTEEN", "FOURTEENTH"),
    (15, "FIFTEEN", "FIFTEENTH"),
    (16, "SIXTEEN", "SIXTEENTH"),
    (17, "SEVENTEEN", "SEVENTEENTH"),
    (18, "EIGHTEEN", "EIGHTEENTH"),
    (19, "NINETEEN", "NINETEENTH"),
    (20, "TWENTY", "TWENTIETH"),
    (30, "THIRTY", "THIRTIETH"),
    (40, "FORTY", "FORTIETH"),
    (50, "FIFTY", "FIFTIETH"),
    (60, "SIXTY", "SIXTIETH"),
    (70, "SEVENTY", "SEVENTIETH"),
    (80, "EIGHTY", "EIGHTIETH"),
    (90, "NINETY", "NINETIETH"),
]


_PERIODS_RAW = [
    (1, "THOUSAND"),
    (2, "MILLION"),
    (3, "BILLION"),
    (4, "TRILLION"),
    (5, "QUADRILLION"),
    (6, "QUINTILLION"),
]


N_TO_CARDINAL, N_TO_ORDINAL = typing.cast(
    typing.Tuple[typing.Dict[Number, str], ...],
    map(dict, zip(*map(_make_map_raw(False), _PARTS_RAW))),
)
N_TO_CARDINAL_PERIOD, N_TO_ORDINAL_PERIOD = typing.cast(
    typing.Tuple[typing.Dict[Number, str], ...],
    map(dict, zip(*map(_make_map_raw(True), map(_map_period_raw, _PERIODS_RAW)))),
)
N_TO_ZERO = {
    Number(0, False, False, False): "ZERO",
    Number(0, True, False, False): "ZEROTH",
}
N_TO_HUNDRED = {
    Number(100, False, False, False): "HUNDRED",
    Number(100, True, False, False): "HUNDREDTH",
}

CARDINAL_TO_N = _reverse_mapping(N_TO_CARDINAL)
ORDINAL_TO_N = _reverse_mapping(N_TO_ORDINAL)
CARDINAL_PERIOD_TO_N = _reverse_mapping(N_TO_CARDINAL_PERIOD)
ORDINAL_PERIOD_TO_N = _reverse_mapping(N_TO_ORDINAL_PERIOD)

ZERO_TO_N = _reverse_mapping(N_TO_ZERO)
HUNDRED_TO_N = _reverse_mapping(N_TO_HUNDRED)


N_LOOKUPS = [
    CARDINAL_TO_N,
    ORDINAL_TO_N,
    CARDINAL_PERIOD_TO_N,
    ORDINAL_PERIOD_TO_N,
    ZERO_TO_N,
    HUNDRED_TO_N,
]

WORD_LOOKUPS = [
    N_TO_CARDINAL,
    N_TO_ORDINAL,
    N_TO_CARDINAL_PERIOD,
    N_TO_ORDINAL_PERIOD,
    N_TO_ZERO,
    N_TO_HUNDRED,
]
