"""CLI utility for nth."""
import argparse
import enum
import logging
import textwrap
from contextlib import suppress

import rich.logging
from rich import print

import nth

# import os
# import readline  # type: ignore


# def run_cardinalize(args: argparse.Namespace):
#     params = nth.DecimalizeParams(
#         strict_periods=not args.not_strict_periods,
#         strict_hundreds=not args.not_strict_hundreds,
#         take_and=not args.no_and,
#         ordinal_bounds=not args.no_ordinal_bounds,
#         cardinal=not args.no_cardinal,
#         ordinal=not args.no_ordinal,
#         cardinal_improper=args.improper or args.cardinal_improper,
#         ordinal_improper=args.improper or args.ordinal_improper,
#     )
#
#     with suppress(KeyboardInterrupt, EOFError):
#         while line := input():
#             print(f'"{nth.cardinalize(line, params)}"')
#
#
# def run_decimalize(args: argparse.Namespace):
#     params = nth.DecimalizeParams(
#         strict_periods=not args.not_strict_periods,
#         strict_hundreds=not args.not_strict_hundreds,
#         take_and=not args.no_and,
#         ordinal_bounds=not args.no_ordinal_bounds,
#         cardinal=not args.no_cardinal,
#         ordinal=not args.no_ordinal,
#         cardinal_improper=args.improper or args.cardinal_improper,
#         ordinal_improper=args.improper or args.ordinal_improper,
#     )
#
#     with suppress(KeyboardInterrupt, EOFError):
#         while line := input():
#             print(f'"{nth.decimalize(line, params)}"')
#
#
# def run_check(args: argparse.Namespace):
#     with suppress(KeyboardInterrupt, EOFError):
#         while line := input():
#             print(f'line: "{line}"')
#             for m, f in [
#                 ("      is decimal ordinal:", nth.is_decimal_ordinal),
#                 ("contains decimal ordinal:", nth.contains_decimal_ordinal),
#             ]:
#                 print(m, f(line))


# def setup_subparser(subparser: argparse.ArgumentParser):
#     subparser.add_argument(
#         "-P",
#         dest="not_strict_periods",
#         action="store_true",
#         help="Allow non-strict periods.",
#     )
#     subparser.add_argument(
#         "-H",
#         dest="not_strict_hundreds",
#         action="store_true",
#         help="Allow non-strict hundreds.",
#     )
#     subparser.add_argument(
#         "-A",
#         dest="no_and",
#         action="store_true",
#         help='Disallow "AND" in input.',
#     )
#     subparser.add_argument(
#         "-B",
#         dest="no_ordinal_bounds",
#         action="store_true",
#         help="Don't end numbers at first ordinal part.",
#     )
#     subparser.add_argument(
#         "-ci",
#         dest="cardinal_improper",
#         action="store_true",
#         help="Allow improper cardinal numbers.",
#     )
#     subparser.add_argument(
#         "-oi",
#         dest="ordinal_improper",
#         action="store_true",
#         help="Allow improper ordinal numbers.",
#     )
#     subparser.add_argument(
#         "-i",
#         dest="improper",
#         action="store_true",
#         help="Allow improper numbers (cardinal and ordinal).",
#     )
#     subparser.add_argument(
#         "-C",
#         dest="no_cardinal",
#         action="store_true",
#         help="Don't perform cardinal replacement.",
#     )
#     subparser.add_argument(
#         "-O",
#         dest="no_ordinal",
#         action="store_true",
#         help="Don't perform ordinal replacement.",
#     )


def main(params: nth.NthalizeArgs):
    with suppress(KeyboardInterrupt, EOFError):
        while line := input():
            print(nth.nthalize(line, args))


class Loc(str, enum.Enum):
    DESCRIPTION = (
        """\
For each STDIN line, detects all numbers (cardinal or ordinal) in either:
- Decimal format (e.g. "12", "32nd"), or
- Word format    (e.g. "one", "forty-fourth")
And converts them to the desired format and prints the result to STDOUT.

Output format key:
    c : Decimal cardinals
    C : Word cardinals
    o : Decimal cordinals
    O : Word ordinals\
        """,
    )
    EPILOG = (
        """\
        (Examples) | Decimal        | Word
        ---------- | -------------- | ------------------------------------------
        Cardinal   | "1"   | "23"   | "FOUR"   | "ONE HUNDRED AND NINETY-SEVEN"
        Ordinal    | "1ST" | "23RD" | "FOURTH" | "ONE HUNDRED AND NINETY-SEVENTH"\
        """,
    )
    VERBOSE = "Verbose output (can be specified multiple times)."
    # TO_CARDINAL_DECIMAL = "Output format: decimal cardinals."
    # TO_CARDINAL_WORD = "Output format: word cardinals."
    # TO_ORDINAL_DECIMAL = "Output format: decimal ordinals."
    # TO_ORDINAL_WORD = "Output format: word ordinals."
    FORMAT = ('Output format (one of "c", "C", "o" or "O").',)


TO_KIND_MAP = {
    "c": nth.FormatArg.CARDINAL_DECIMAL,
    "C": nth.FormatArg.CARDINAL_WORD,
    "o": nth.FormatArg.ORDINAL_DECIMAL,
    "O": nth.FormatArg.ORDINAL_WORD,
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "nth",
        description=Loc.DESCRIPTION,
        epilog=textwrap.dedent(Loc.EPILOG),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v",
        dest="verbose",
        action="count",
        default=0,
        help=Loc.VERBOSE,
    )
    parser.add_argument(
        "format",
        metavar="Format",
        choices=["c", "C", "o", "O"],
        help=Loc.FORMAT,
    )
    cli_args = parser.parse_args()
    log_level = max(0, logging.WARNING - 10 * cli_args.verbose)
    logging.basicConfig(
        level=log_level,
        format="(%(pathname)s:%(lineno)d)\n%(message)s",
        handlers=[rich.logging.RichHandler()],
    )
    args = nth.NthalizeArgs(
        format=TO_KIND_MAP[cli_args.format],
        # TODO: cardinal_and config
    )
    main(args)
