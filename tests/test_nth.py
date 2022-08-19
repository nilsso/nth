# pylama:ignore=D100,D101,D102,D103,D104,D107
import typing

import pytest

import nth
import nth.nthalize

INT_INPUT, ORDINAL_INPUT, CARDINAL_EXPECTED, ORDINAL_EXPECTED = typing.cast(
    typing.Tuple[
        typing.List[int],
        typing.List[str],
        typing.List[str],
        typing.List[str],
    ],
    zip(
        *[
            (1, "1ST", "ONE", "FIRST"),
            (2, "2ND", "TWO", "SECOND"),
            (3, "3RD", "THREE", "THIRD"),
            (4, "4TH", "FOUR", "FOURTH"),
            (5, "5TH", "FIVE", "FIFTH"),
            (6, "6TH", "SIX", "SIXTH"),
            (7, "7TH", "SEVEN", "SEVENTH"),
            (8, "8TH", "EIGHT", "EIGHTH"),
            (9, "9TH", "NINE", "NINTH"),
            (10, "10TH", "TEN", "TENTH"),
            (11, "11TH", "ELEVEN", "ELEVENTH"),
            (12, "12TH", "TWELVE", "TWELFTH"),
            (13, "13TH", "THIRTEEN", "THIRTEENTH"),
            (14, "14TH", "FOURTEEN", "FOURTEENTH"),
            (15, "15TH", "FIFTEEN", "FIFTEENTH"),
            (16, "16TH", "SIXTEEN", "SIXTEENTH"),
            (17, "17TH", "SEVENTEEN", "SEVENTEENTH"),
            (18, "18TH", "EIGHTEEN", "EIGHTEENTH"),
            (19, "19TH", "NINETEEN", "NINETEENTH"),
            (20, "20TH", "TWENTY", "TWENTIETH"),
            (21, "21ST", "TWENTY-ONE", "TWENTY-FIRST"),
            (30, "30TH", "THIRTY", "THIRTIETH"),
            (32, "32ND", "THIRTY-TWO", "THIRTY-SECOND"),
            (40, "40TH", "FORTY", "FORTIETH"),
            (43, "43RD", "FORTY-THREE", "FORTY-THIRD"),
            (50, "50TH", "FIFTY", "FIFTIETH"),
            (54, "54TH", "FIFTY-FOUR", "FIFTY-FOURTH"),
            (60, "60TH", "SIXTY", "SIXTIETH"),
            (65, "65TH", "SIXTY-FIVE", "SIXTY-FIFTH"),
            (70, "70TH", "SEVENTY", "SEVENTIETH"),
            (76, "76TH", "SEVENTY-SIX", "SEVENTY-SIXTH"),
            (80, "80TH", "EIGHTY", "EIGHTIETH"),
            (87, "87TH", "EIGHTY-SEVEN", "EIGHTY-SEVENTH"),
            (90, "90TH", "NINETY", "NINETIETH"),
            (98, "98TH", "NINETY-EIGHT", "NINETY-EIGHTH"),
            (100, "100TH", "ONE HUNDRED", "ONE HUNDREDTH"),
            (101, "101ST", "ONE HUNDRED ONE", "ONE HUNDRED FIRST"),
            (122, "122ND", "ONE HUNDRED TWENTY-TWO", "ONE HUNDRED TWENTY-SECOND"),
            (133, "133RD", "ONE HUNDRED THIRTY-THREE", "ONE HUNDRED THIRTY-THIRD"),
            (230, "230TH", "TWO HUNDRED THIRTY", "TWO HUNDRED THIRTIETH"),
            (456, "456TH", "FOUR HUNDRED FIFTY-SIX", "FOUR HUNDRED FIFTY-SIXTH"),
            (999, "999TH", "NINE HUNDRED NINETY-NINE", "NINE HUNDRED NINETY-NINTH"),
            (1000, "1000TH", "ONE THOUSAND", "ONE THOUSANDTH"),
            (2050, "2050TH", "TWO THOUSAND FIFTY", "TWO THOUSAND FIFTIETH"),
            (
                132_456,
                "132456TH",
                "ONE HUNDRED THIRTY-TWO THOUSAND FOUR HUNDRED FIFTY-SIX",
                "ONE HUNDRED THIRTY-TWO THOUSAND FOUR HUNDRED FIFTY-SIXTH",
            ),
            (
                965_302_219_560_189_405_377,
                "965302219560189405377TH",
                (
                    "NINE HUNDRED SIXTY-FIVE QUINTILLION"
                    " THREE HUNDRED TWO QUADRILLION"
                    " TWO HUNDRED NINETEEN TRILLION"
                    " FIVE HUNDRED SIXTY BILLION"
                    " ONE HUNDRED EIGHTY-NINE MILLION"
                    " FOUR HUNDRED FIVE THOUSAND"
                    " THREE HUNDRED SEVENTY-SEVEN"
                ),
                (
                    "NINE HUNDRED SIXTY-FIVE QUINTILLION"
                    " THREE HUNDRED TWO QUADRILLION"
                    " TWO HUNDRED NINETEEN TRILLION"
                    " FIVE HUNDRED SIXTY BILLION"
                    " ONE HUNDRED EIGHTY-NINE MILLION"
                    " FOUR HUNDRED FIVE THOUSAND"
                    " THREE HUNDRED SEVENTY-SEVENTH"
                ),
            ),
        ]
    ),
)


INT_TO_CARDINAL_PARAMS = zip(INT_INPUT, CARDINAL_EXPECTED)


@pytest.mark.parametrize("n,expected", INT_TO_CARDINAL_PARAMS)
def test_int_to_cardinal(n: int, expected: str):
    assert nth.cardinalize(str(n), as_word=True) == expected.replace("-", " ")


# INT_TO_ORDINAL_PARAMS = zip(INT_INPUT, ORDINAL_EXPECTED)
#
#
# @pytest.mark.parametrize("n,expected", INT_TO_ORDINAL_PARAMS)
# def test_int_to_ordinal(n: int, expected: str):
#     assert nth.int_to_ordinal(n) == expected
#
#
# SUFFIXES = {"ST", "ND", "RD", "TH"}
#
#
# NORMALIZE_ORDINAL_STRICT_PARAMS = [
#     *zip(ORDINAL_INPUT, ORDINAL_EXPECTED),
#     *[
#         (f"{n[:-2]}{bad_suffix}", None)
#         for n in ORDINAL_INPUT
#         for bad_suffix in SUFFIXES - {n[-2:]}
#     ],
# ]
#
#
# @pytest.mark.parametrize("n,expected", NORMALIZE_ORDINAL_STRICT_PARAMS)
# def test_normalize_ordinal_strict(n: str, expected: str):
#     assert nth.try_normalize_ordinal(n, True) == expected
#
#
# NORMALIZE_ORDINAL_NONSTRICT_PARAMS = [
#     *[
#         (f"{n[:-2]}{suffix}", expected)
#         for n, expected in zip(ORDINAL_INPUT, ORDINAL_EXPECTED)
#         for suffix in SUFFIXES
#     ]
# ]
#
#
# @pytest.mark.parametrize("n,expected", NORMALIZE_ORDINAL_NONSTRICT_PARAMS)
# def test_normalize_ordinal_nonstrict(n: str, expected: str):
#     assert nth.try_normalize_ordinal(n) == expected
#
#
# @pytest.mark.parametrize("n,expect", zip(map(str, INT_INPUT), ORDINAL_INPUT))
# def test_digit_ordinalize(n: str, expect: str):
#     assert nth.try_digit_ordinal_to_word(n) == expect
#
#
# @pytest.mark.parametrize("s,expect", zip(ORDINAL_EXPECTED, ORDINAL_INPUT))
# def test_decimalize(s: str, expect: str):
#     assert nth.decimalize(s) == expect
