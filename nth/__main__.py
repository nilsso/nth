"""CLI utility for nth."""
import argparse
import logging
import os
import readline  # type: ignore
from contextlib import suppress

import rich.logging
from rich import print

import nth


def run_cardinalize(args: argparse.Namespace):
    params = nth.DecimalizeParams(
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
            print(f'"{nth.cardinalize(line, params)}"')


def run_decimalize(args: argparse.Namespace):
    params = nth.DecimalizeParams(
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
            print(f'"{nth.decimalize(line, params)}"')


def run_check(args: argparse.Namespace):
    with suppress(KeyboardInterrupt, EOFError):
        while line := input():
            print(f'line: "{line}"')
            for m, f in [
                ("      is decimal ordinal:", nth.is_decimal_ordinal),
                ("contains decimal ordinal:", nth.contains_decimal_ordinal),
            ]:
                print(m, f(line))


def setup_subparser(subparser: argparse.ArgumentParser):
    subparser.add_argument(
        "-P",
        dest="not_strict_periods",
        action="store_true",
        help="Allow non-strict periods.",
    )
    subparser.add_argument(
        "-H",
        dest="not_strict_hundreds",
        action="store_true",
        help="Allow non-strict hundreds.",
    )
    subparser.add_argument(
        "-A",
        dest="no_and",
        action="store_true",
        help='Disallow "AND" in input.',
    )
    subparser.add_argument(
        "-B",
        dest="no_ordinal_bounds",
        action="store_true",
        help="Don't end numbers at first ordinal part.",
    )
    subparser.add_argument(
        "-ci",
        dest="cardinal_improper",
        action="store_true",
        help="Allow improper cardinal numbers.",
    )
    subparser.add_argument(
        "-oi",
        dest="ordinal_improper",
        action="store_true",
        help="Allow improper ordinal numbers.",
    )
    subparser.add_argument(
        "-i",
        dest="improper",
        action="store_true",
        help="Allow improper numbers (cardinal and ordinal).",
    )
    subparser.add_argument(
        "-C",
        dest="no_cardinal",
        action="store_true",
        help="Don't perform cardinal replacement.",
    )
    subparser.add_argument(
        "-O",
        dest="no_ordinal",
        action="store_true",
        help="Don't perform ordinal replacement.",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="verbose", action="count", default=0)

    subparsers = parser.add_subparsers()

    check_parser = subparsers.add_parser("check")
    check_parser.set_defaults(func=run_check)

    cardinalize_parser = subparsers.add_parser("card")
    cardinalize_parser.set_defaults(func=run_cardinalize)
    setup_subparser(cardinalize_parser)

    decimalize_parser = subparsers.add_parser("dec")
    decimalize_parser.set_defaults(func=run_decimalize)
    setup_subparser(decimalize_parser)

    args = parser.parse_args()
    log_level = max(0, logging.INFO - 10 * args.verbose)
    logging.basicConfig(
        level=log_level,
        format="(%(pathname)s:%(lineno)d)\n%(message)s",
        handlers=[rich.logging.RichHandler()],
    )
    args.func(args)
