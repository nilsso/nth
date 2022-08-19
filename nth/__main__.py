"""CLI utility for nth."""
import argparse
import logging
import re
import textwrap
import typing
from contextlib import suppress

import rich.logging
from rich import print
from rich_argparse import RichHelpFormatter  # type: ignore

import nth
import nth.nthalize
from nth.nthalize import nthalize as _nthalize

DEFAULT_LOG_LEVEL = logging.INFO


def _log_level(n: int):
    return DEFAULT_LOG_LEVEL - 10 * n


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
    convert_arg_interactive: str


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
    convert_arg_format="Output format.",
    convert_arg_interactive="Interactive mode.",
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


VERBOSE_P = re.compile(r"/v(\d+)")


def _nth_convert(args: argparse.Namespace):
    if not args.interactive:
        _n, _f = TO_KIND_MAP[args.format]

        nthalize_args = nth.NthalizeArgs(
            number=_n,
            format=_f,
            word_behavior=None,
        )
        with suppress(KeyboardInterrupt, EOFError):
            while line := input():
                print(_nthalize(line, nthalize_args))
    else:
        import readline  # type: ignore

        nth_logger = nth.nthalize.logger
        main_logger = logging.getLogger(__name__)
        main_logger.setLevel(logging.INFO)

        _c = nth.NthalizeArgs(number="CARDINAL", format="DECIMAL", word_behavior=None)
        _C = nth.NthalizeArgs(number="CARDINAL", format="WORD", word_behavior=None)
        _o = nth.NthalizeArgs(number="ORDINAL", format="DECIMAL", word_behavior=None)
        _O = nth.NthalizeArgs(number="ORDINAL", format="WORD", word_behavior=None)
        FORMATS = {
            "/c": (_c, "cardinal decimal"),
            "/C": (_C, "cardinal word"),
            "/o": (_o, "ordinal decimal"),
            "/O": (_O, "ordinal word"),
        }
        FORMAT_KEYS = list(FORMATS.keys())

        nthalize_args = nth.nthalize.default_args()

        with suppress(KeyboardInterrupt, EOFError):
            while line := input():
                match line:
                    case s if (m := VERBOSE_P.fullmatch(s)) is not None:
                        n = _log_level(int(m.group(1)))
                        nth_logger.setLevel(n)
                        main_logger.info(f"log level set to {n}")
                        pass
                    case s if s in FORMAT_KEYS:
                        format, msg = FORMATS[s]
                        nthalize_args.update(format)
                        main_logger.info(f"format changed to {msg}")
                    case _:
                        print(_nthalize(line, nthalize_args))


def main():
    """Main driver function."""
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
    detect_parser.set_defaults(func=_nth_detect)
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
    convert_parser.set_defaults(func=_nth_convert)
    convert_mode_group = convert_parser.add_mutually_exclusive_group(required=True)
    convert_mode_group.add_argument(
        "-f",
        "--format",
        choices=["c", "C", "o", "O"],
        help=loc["convert_arg_format"],
    )
    convert_mode_group.add_argument(
        "-i",
        "--interactive",
        action="store_true",
        help=loc["convert_arg_interactive"],
    )

    # ------------------------------------------------------------------------------------
    args = parser.parse_args()

    log_level = _log_level(args.verbose)
    logging.basicConfig(
        level=log_level,
        format="(%(pathname)s:%(lineno)d)\n%(message)s",
        handlers=[rich.logging.RichHandler()],
    )

    args.func(args)


if __name__ == "__main__":
    main()
