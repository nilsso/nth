import pytest

import nth

# "A1 Sauce"


@pytest.mark.parametrize(
    "s,expect",
    [
        ("1 2 3 4 5", False),
        ("1 2 3rd 4 5", True),
    ],
)
def test_contains_ordinal_decimal(s: str, expect: bool):
    assert nth.nthalize.contains_ordinal_decimal(s) == expect
