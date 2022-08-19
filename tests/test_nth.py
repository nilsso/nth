# pylama:ignore=D100,D101,D102,D103,D104,D107
import typing

import pytest

import nth
import nth.nthalize

_RAW_PARAMS = [
    ("1", "1ST", "ONE", "FIRST"),
    ("2", "2ND", "TWO", "SECOND"),
    ("3", "3RD", "THREE", "THIRD"),
    ("4", "4TH", "FOUR", "FOURTH"),
    ("5", "5TH", "FIVE", "FIFTH"),
    ("6", "6TH", "SIX", "SIXTH"),
    ("7", "7TH", "SEVEN", "SEVENTH"),
    ("8", "8TH", "EIGHT", "EIGHTH"),
    ("9", "9TH", "NINE", "NINTH"),
    ("10", "10TH", "TEN", "TENTH"),
    ("11", "11TH", "ELEVEN", "ELEVENTH"),
    ("12", "12TH", "TWELVE", "TWELFTH"),
    ("13", "13TH", "THIRTEEN", "THIRTEENTH"),
    ("14", "14TH", "FOURTEEN", "FOURTEENTH"),
    ("15", "15TH", "FIFTEEN", "FIFTEENTH"),
    ("16", "16TH", "SIXTEEN", "SIXTEENTH"),
    ("17", "17TH", "SEVENTEEN", "SEVENTEENTH"),
    ("18", "18TH", "EIGHTEEN", "EIGHTEENTH"),
    ("19", "19TH", "NINETEEN", "NINETEENTH"),
    ("20", "20TH", "TWENTY", "TWENTIETH"),
    ("21", "21ST", "TWENTY-ONE", "TWENTY-FIRST"),
    ("30", "30TH", "THIRTY", "THIRTIETH"),
    ("32", "32ND", "THIRTY-TWO", "THIRTY-SECOND"),
    ("40", "40TH", "FORTY", "FORTIETH"),
    ("43", "43RD", "FORTY-THREE", "FORTY-THIRD"),
    ("50", "50TH", "FIFTY", "FIFTIETH"),
    ("54", "54TH", "FIFTY-FOUR", "FIFTY-FOURTH"),
    ("60", "60TH", "SIXTY", "SIXTIETH"),
    ("65", "65TH", "SIXTY-FIVE", "SIXTY-FIFTH"),
    ("70", "70TH", "SEVENTY", "SEVENTIETH"),
    ("76", "76TH", "SEVENTY-SIX", "SEVENTY-SIXTH"),
    ("80", "80TH", "EIGHTY", "EIGHTIETH"),
    ("87", "87TH", "EIGHTY-SEVEN", "EIGHTY-SEVENTH"),
    ("90", "90TH", "NINETY", "NINETIETH"),
    ("98", "98TH", "NINETY-EIGHT", "NINETY-EIGHTH"),
    ("100", "100TH", "ONE HUNDRED", "ONE HUNDREDTH"),
    ("101", "101ST", "ONE HUNDRED ONE", "ONE HUNDRED FIRST"),
    ("122", "122ND", "ONE HUNDRED TWENTY-TWO", "ONE HUNDRED TWENTY-SECOND"),
    ("133", "133RD", "ONE HUNDRED THIRTY-THREE", "ONE HUNDRED THIRTY-THIRD"),
    ("230", "230TH", "TWO HUNDRED THIRTY", "TWO HUNDRED THIRTIETH"),
    ("456", "456TH", "FOUR HUNDRED FIFTY-SIX", "FOUR HUNDRED FIFTY-SIXTH"),
    ("999", "999TH", "NINE HUNDRED NINETY-NINE", "NINE HUNDRED NINETY-NINTH"),
    ("1000", "1000TH", "ONE THOUSAND", "ONE THOUSANDTH"),
    ("2050", "2050TH", "TWO THOUSAND FIFTY", "TWO THOUSAND FIFTIETH"),
    (
        "132456",
        "132456TH",
        "ONE HUNDRED THIRTY-TWO THOUSAND FOUR HUNDRED FIFTY-SIX",
        "ONE HUNDRED THIRTY-TWO THOUSAND FOUR HUNDRED FIFTY-SIXTH",
    ),
    (
        "1234567890987654321",
        "1234567890987654321ST",
        (
            "ONE QUINTILLION"
            " TWO HUNDRED THIRTY-FOUR QUADRILLION"
            " FIVE HUNDRED SIXTY-SEVEN TRILLION"
            " EIGHT HUNDRED NINETY BILLION"
            " NINE HUNDRED EIGHTY-SEVEN MILLION"
            " SIX HUNDRED FIFTY-FOUR THOUSAND"
            " THREE HUNDRED TWENTY-ONE"
        ),
        (
            "ONE QUINTILLION"
            " TWO HUNDRED THIRTY-FOUR QUADRILLION"
            " FIVE HUNDRED SIXTY-SEVEN TRILLION"
            " EIGHT HUNDRED NINETY BILLION"
            " NINE HUNDRED EIGHTY-SEVEN MILLION"
            " SIX HUNDRED FIFTY-FOUR THOUSAND"
            " THREE HUNDRED TWENTY-FIRST"
        ),
    ),
]

CARDINAL, ORDINAL, CARDINAL_WORD, ORDINAL_WORD = L_PARAMS = list(
    typing.cast(
        typing.Iterator[list[str]],
        map(list, zip(*_RAW_PARAMS)),
    )
)


R_PARAMS = [
    (CARDINAL, False, nth.cardinalize),
    (ORDINAL, False, nth.ordinalize),
    (CARDINAL_WORD, True, nth.cardinalize),
    (ORDINAL_WORD, True, nth.ordinalize),
]


class Truncate:
    max_width: int
    tail_width: int

    def __init__(self, max_width: int, tail_width: int):
        self.max_width = max_width
        self.tail_width = tail_width

    def __call__(self, s: str) -> str:
        if len(s) < self.max_width:
            return s
        i = self.max_width - self.tail_width
        j = self.tail_width
        return f"{s[:i]}...{s[-j:]}"


TRUNCATE = Truncate(40, 8)


class ExhaustiveParam(typing.NamedTuple):
    v: str
    expected: str
    as_word: bool
    f: typing.Callable[[str, bool], str]

    def __str__(self) -> str:
        fmt = "as-word" if self.as_word else "as-decimal"
        v = TRUNCATE(self.v)
        return f'{self.f.__name__}-{fmt}-"{v}"'

    # @staticmethod
    # def from_params(
    #     l_params,
    #     r_params,
    # ):
    #     for _expect, as_word, f in l_params:
    #         for _v in r_params:
    #             for v, expect in zip(_v, _expect):
    #                 yield ExhaustiveParam(v, expect, as_word, f)


def exhaustive_params():
    for _expect, as_word, f in R_PARAMS:
        for _v in L_PARAMS:
            for v, expect in zip(_v, _expect):
                yield ExhaustiveParam(v, expect, as_word, f)


def _test_exhaustive(p: ExhaustiveParam):
    lhs = p.f(str(p.v), p.as_word)
    rhs = str(p.expected).replace("-", " ")
    print(f"{lhs=}")
    print(f"{rhs=}")
    assert lhs == rhs


# @pytest.mark.parametrize("p", ExhaustiveParam.from_params(L_PARAMS, R_PARAMS), ids=str)
@pytest.mark.parametrize("p", exhaustive_params(), ids=str)
def test_exhaustive(
    p: ExhaustiveParam,
):
    _test_exhaustive(p)
