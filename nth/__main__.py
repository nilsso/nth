"""CLI utility for nth."""
import argparse
import readline  # type: ignore
from contextlib import suppress

from . import DecimalizeParams, decimalize


def run_decimalize(args: argparse.Namespace):
    params = DecimalizeParams(
        strict_periods=not args.not_strict_periods,
        strict_hundreds=not args.not_strict_hundreds,
        take_and=not args.no_and,
        ordinal_bounds=not args.no_ordinal_bounds,
        cardinal=not args.no_cardinal,
        ordinal=not args.no_ordinal,
        cardinal_improper=args.improper or args.cardinal_improper,
        ordinal_improper=args.improper or args.ordinal_improper,
    )

    with suppress(KeyboardInterrupt, EOFError):
        while line := input():
            print(f'"{decimalize(line, params)}"')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers()

    decimalize_parser = subparsers.add_parser("dec")
    decimalize_parser.set_defaults(func=run_decimalize)
    decimalize_parser.add_argument(
        "-P",
        dest="not_strict_periods",
        action="store_true",
        help="Allow non-strict periods.",
    )
    decimalize_parser.add_argument(
        "-H",
        dest="not_strict_hundreds",
        action="store_true",
        help="Allow non-strict hundreds.",
    )
    decimalize_parser.add_argument(
        "-A",
        dest="no_and",
        action="store_true",
        help='Disallow "AND" in input.',
    )
    decimalize_parser.add_argument(
        "-B",
        dest="no_ordinal_bounds",
        action="store_true",
        help="Don't end numbers at first ordinal part.",
    )
    decimalize_parser.add_argument(
        "-ci",
        dest="cardinal_improper",
        action="store_true",
        help="Allow improper cardinal numbers.",
    )
    decimalize_parser.add_argument(
        "-oi",
        dest="ordinal_improper",
        action="store_true",
        help="Allow improper ordinal numbers.",
    )
    decimalize_parser.add_argument(
        "-i",
        dest="improper",
        action="store_true",
        help="Allow improper numbers (cardinal and ordinal).",
    )
    decimalize_parser.add_argument(
        "-C",
        dest="no_cardinal",
        action="store_true",
        help="Don't perform cardinal replacement.",
    )
    decimalize_parser.add_argument(
        "-O",
        dest="no_ordinal",
        action="store_true",
        help="Don't perform ordinal replacement.",
    )

    rollyear = 2021

    args = parser.parse_args()
    args.func(args)
