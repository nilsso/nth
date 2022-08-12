"""Integer to cardinal/ordinal (or vice versa) lookup tables."""
import typing

A = typing.TypeVar("A")
B = typing.TypeVar("B")


def _reverse_mapping(mapping: typing.Mapping[A, B]) -> typing.Dict[B, A]:
    return {b: a for a, b in mapping.items()}


INT_TO_CARDINAL = {
    # 0: "ZERO",
    1: "ONE",
    2: "TWO",
    3: "THREE",
    4: "FOUR",
    5: "FIVE",
    6: "SIX",
    7: "SEVEN",
    8: "EIGHT",
    9: "NINE",
    10: "TEN",
    11: "ELEVEN",
    12: "TWELVE",
    13: "THIRTEEN",
    14: "FOURTEEN",
    15: "FIFTEEN",
    16: "SIXTEEN",
    17: "SEVENTEEN",
    18: "EIGHTEEN",
    19: "NINETEEN",
    20: "TWENTY",
    30: "THIRTY",
    40: "FORTY",
    50: "FIFTY",
    60: "SIXTY",
    70: "SEVENTY",
    80: "EIGHTY",
    90: "NINETY",
}


INT_TO_ORDINAL = {
    1: "FIRST",
    2: "SECOND",
    3: "THIRD",
    4: "FOURTH",
    5: "FIFTH",
    6: "SIXTH",
    7: "SEVENTH",
    8: "EIGHTH",
    9: "NINTH",
    10: "TENTH",
    11: "ELEVENTH",
    12: "TWELFTH",
    # TODO:
    # consider "corrections" table
    # "TWELVTH
    # "TWELVETH
    13: "THIRTEENTH",
    14: "FOURTEENTH",
    15: "FIFTEENTH",
    16: "SIXTEENTH",
    17: "SEVENTEENTH",
    18: "EIGHTEENTH",
    19: "NINETEENTH",
    20: "TWENTIETH",
    30: "THIRTIETH",
    40: "FORTIETH",
    50: "FIFTIETH",
    60: "SIXTIETH",
    70: "SEVENTIETH",
    80: "EIGHTIETH",
    90: "NINETIETH",
}

INT_TO_PERIOD = {
    1: "THOUSAND",
    2: "MILLION",
    3: "BILLION",
    4: "TRILLION",
    5: "QUADRILLION",
    6: "QUINTILLION",
}

CARDINAL_TO_INT = _reverse_mapping(INT_TO_CARDINAL)
ORDINAL_TO_INT = _reverse_mapping(INT_TO_ORDINAL)
PERIOD_TO_INT = _reverse_mapping(INT_TO_PERIOD)
