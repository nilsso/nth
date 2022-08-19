"""CLI utility for nth."""
import argparse
import logging
import textwrap
import typing
from contextlib import suppress

import rich.logging
from rich import print
from rich_argparse import RichHelpFormatter  # type: ignore

import nth
import nth.nthalize
from nth.nthalize import nthalize as _nthalize

DEFAULT_LOG_LEVEL = logging.WARNING


def _strip_dedent(s: str) -> str:
    return textwrap.dedent(s).strip()


class Locale(typing.TypedDict):
    """Locale."""

    # base command
    help: str
    help_epilog: str
    arg_verbose: str
    # detect subcommand
    detect_help: str
    detect_description: str
    detect_arg_input: str
    # convert subcommand
    convert_help: str
    convert_description: str
    convert_epilog: str
    convert_arg_format: str


LOC_EN_US: Locale = Locale(
    # ------------------------------------------------------------------------------------
    # base command
    # ------------------------------------------------------------------------------------
    help=_strip_dedent(
        """
        Utility for detecting and converting numbers.

        A "number" can be in any cardinal or ordinal, decimal or word format.
        (See epilog for examples on these terms.)

        See "nth {cmd} -h" for subcommand help.
        """
    ),
    help_epilog=_strip_dedent(
        """
        (Examples) | Decimal        | Word
        ---------- | -------------- | -------------------------------------------
        Cardinal   | "1"   | "23"   | "FOUR"   | "ONE HUNDRED AND NINETY-SEVEN"
        Ordinal    | "1ST" | "23RD" | "FOURTH" | "ONE HUNDRED AND NINETY-SEVENTH"
        """
    ),
    arg_verbose="Verbose output (can be specified multiple times).",
    # ------------------------------------------------------------------------------------
    # detect subcommand
    # ------------------------------------------------------------------------------------
    detect_help="Detect numbers within a string.",
    detect_description=(
        "Return 1 if input string contains any number-like sequences"
        " according to the filter parameters, else 0."
    ),
    detect_arg_input="Input string.",
    # ------------------------------------------------------------------------------------
    # convert subcommand
    # ------------------------------------------------------------------------------------
    convert_help="Convert numbers within STDIN lines.",
    convert_description=(
        "For each STDIN line, converts all number-like sequences into"
        " the desired format and outputs the converted line to STDOUT."
        "\n\n"
        "(See epilog for format descriptions.)"
    ),
    convert_epilog=_strip_dedent(
        """
        FORMAT | Description
        ------ | ------------------
        "c"    | Decimal cardinals.
        "C"    | Word cardinals.
        "o"    | Decimal cordinals.
        "O"    | Word ordinals.
        """
    ),
    convert_arg_format='Output format (one of "c", "C", "o" or "O").',
)

LOCALES = {
    "enUS": LOC_EN_US,
}


TO_KIND_MAP = {
    "c": ("CARDINAL", "DECIMAL"),
    "C": ("CARDINAL", "WORD"),
    "o": ("ORDINAL", "DECIMAL"),
    "O": ("ORDINAL", "WORD"),
}


def _nth_detect(args: argparse.Namespace):
    # TODO: filter parameters
    print(nth.nthalize.contains_numbers(args.input))


def _nth_convert(args: argparse.Namespace):
    _n, _f = TO_KIND_MAP[args.format]
    nthalize_args = nth.NthalizeArgs(
        number=_n,
        format=_f,
        word_behavior=None,
    )
    with suppress(KeyboardInterrupt, EOFError):
        while line := input():
            print(_nthalize(line, nthalize_args))


def main():
    loc: Locale = LOCALES["enUS"]

    # ------------------------------------------------------------------------------------
    # base command
    # ------------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(
        __name__.removesuffix(".__main__"),
        formatter_class=RichHelpFormatter,
        description=loc["help"],
        epilog=loc["help_epilog"],
    )

    parser.add_argument(
        "-v",
        dest="verbose",
        action="count",
        default=0,
        help=loc["arg_verbose"],
    )

    subparsers = parser.add_subparsers(metavar="cmd")

    # ------------------------------------------------------------------------------------
    # detect subcommand
    # ------------------------------------------------------------------------------------
    detect_parser = subparsers.add_parser(
        "detect",
        help=loc["detect_help"],
        description=loc["detect_description"],
        formatter_class=RichHelpFormatter,
    )
    detect_parser.set_defaults(f=_nth_detect)
    detect_parser.add_argument(
        "input",
        metavar="INPUT",
        help=loc["detect_arg_input"],
    )

    # ------------------------------------------------------------------------------------
    # convert subcommand
    # ------------------------------------------------------------------------------------
    convert_parser = subparsers.add_parser(
        "convert",
        help=loc["convert_help"],
        description=loc["convert_description"],
        epilog=loc["convert_epilog"],
        formatter_class=RichHelpFormatter,
    )
    convert_parser.set_defaults(f=_nth_convert)
    convert_parser.add_argument(
        "format",
        metavar="FORMAT",
        choices=["c", "C", "o", "O"],
        help=loc["convert_arg_format"],
    )

    # ------------------------------------------------------------------------------------
    args = parser.parse_args()

    log_level = DEFAULT_LOG_LEVEL - 10 * args.verbose
    logging.basicConfig(
        level=log_level,
        format="(%(pathname)s:%(lineno)d)\n%(message)s",
        handlers=[rich.logging.RichHandler()],
    )

    args.f(args)


if __name__ == "__main__":
    main()
