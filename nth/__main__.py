import tyro
from rich.console import Console

from . import ordinalize


def main(s: str, /) -> None:
    console = Console()
    console.print(ordinalize(s))


tyro.cli(main)


# """CLI utility for nth."""
# import argparse
# import logging
# import re
# import textwrap
# import typing
# from contextlib import suppress
#
# import nth
# import nth.nthalize
# from nth.nthalize import nthalize as _nthalize
#
# DEFAULT_LOG_LEVEL = logging.INFO
# HISTORY_PATH = "/tmp/nth_history"
#
#
# def _strip_dedent(s: str) -> str:
#     return textwrap.dedent(s).strip()
#
#
# class Locale(typing.TypedDict):
#     """Locale."""
#
#     # base command
#     help: str
#     help_epilog: str
#     arg_verbose: str
#     # detect subcommand
#     detect_help: str
#     detect_description: str
#     detect_arg_input: str
#     # convert subcommand
#     convert_help: str
#     convert_description: str
#     convert_epilog: str
#     convert_arg_format: str
#     convert_arg_interactive: str
#     # convert interactive
#     convert_interactive_help: str
#     convert_interactive_help_extended: str
#
#
# LOC_EN_US: Locale = Locale(
#     # ------------------------------------------------------------------------------------
#     # base command
#     # ------------------------------------------------------------------------------------
#     help=_strip_dedent(
#         """
#         Utility for detecting and converting numbers.
#
#         A "number" can be in any cardinal or ordinal, decimal or word format.
#         (See epilog for examples on these terms.)
#
#         See "nth {cmd} -h" for subcommand help.
#         """
#     ),
#     help_epilog=_strip_dedent(
#         """
#         (Examples) | Decimal        | Word
#         ---------- | -------------- | -------------------------------------------
#         Cardinal   | "1"   | "23"   | "FOUR"   | "ONE HUNDRED AND NINETY-SEVEN"
#         Ordinal    | "1ST" | "23RD" | "FOURTH" | "ONE HUNDRED AND NINETY-SEVENTH"
#         """
#     ),
#     arg_verbose="Verbose output (can be specified multiple times).",
#     # ------------------------------------------------------------------------------------
#     # detect subcommand
#     # ------------------------------------------------------------------------------------
#     detect_help="Detect numbers within a string.",
#     detect_description=(
#         "Return 1 if input string contains any number-like sequences"
#         " according to the filter parameters, else 0."
#     ),
#     detect_arg_input="Input string.",
#     # ------------------------------------------------------------------------------------
#     # convert subcommand
#     # ------------------------------------------------------------------------------------
#     convert_help="Convert numbers within STDIN lines.",
#     convert_description=(
#         "For each STDIN line, converts all number-like sequences into"
#         " the desired format and outputs the converted line to STDOUT."
#         "\n\n"
#         "(See epilog for format descriptions.)"
#     ),
#     convert_epilog=_strip_dedent(
#         """
#         FORMAT | Description
#         ------ | ------------------
#         "c"    | Decimal cardinals.
#         "C"    | Word cardinals.
#         "o"    | Decimal cordinals.
#         "O"    | Word ordinals.
#         """
#     ),
#     convert_arg_format="Output format.",
#     convert_arg_interactive="Interactive mode.",
#     convert_interactive_help=_strip_dedent(
#         """
#         nth convert interactive mode commands:
#             "/h"    : Print this help message
#             "/c"    : Set format to cardinal decimal.
#             "/C"    : Set format to cardinal word.
#             "/o"    : Set format to ordinal decimal.
#             "/O"    : Set format to ordinal word.
#             "/v(n)" : Set log level to {n}.
#         to quit: CTRL-C/CTRL-D
#         """
#     ),
#     convert_interactive_help_extended=_strip_dedent(
#         """
#         additionally:
#         - up/down arrows scroll through history
#         - history is stored in "/tmp/nth_history"
#         """
#     ),
# )
#
# LOCALES = {
#     "enUS": LOC_EN_US,
# }
#
#
# def _nth_detect(_: Locale, args: argparse.Namespace):
#     # TODO: filter parameters
#     print(nth.nthalize.contains_numbers(args.input))
#
#
# def _nth_convert(loc: Locale, args: argparse.Namespace):
#     if args.interactive:
#         _nth_convert_interactive(loc)
#     else:
#         _nth_convert_stdin(loc, args)
#
#
# def _nth_convert_stdin(_: Locale, args: argparse.Namespace):
#     TO_KIND_MAP = {
#         "c": ("CARDINAL", "DECIMAL"),
#         "C": ("CARDINAL", "WORD"),
#         "o": ("ORDINAL", "DECIMAL"),
#         "O": ("ORDINAL", "WORD"),
#     }
#     _n, _f = TO_KIND_MAP[args.format]
#
#     nthalize_args = nth.NthalizeArgs(
#         number=_n,
#         format=_f,
#         word_behavior=None,
#     )
#     with suppress(KeyboardInterrupt, EOFError):
#         while line := input():
#             print(_nthalize(line, nthalize_args))
#
#
# def _nth_convert_interactive(loc: Locale):
#     import readline
#
#     open(HISTORY_PATH, "a").close()
#     readline.read_history_file(HISTORY_PATH)
#
#     nth_logger = nth.nthalize.logger
#
#     _c = nth.NthalizeArgs(number="CARDINAL", format="DECIMAL", word_behavior=None)
#     _C = nth.NthalizeArgs(number="CARDINAL", format="WORD", word_behavior=None)
#     _o = nth.NthalizeArgs(number="ORDINAL", format="DECIMAL", word_behavior=None)
#     _O = nth.NthalizeArgs(number="ORDINAL", format="WORD", word_behavior=None)
#     FORMATS = {
#         "/c": (_c, "cardinal decimal"),
#         "/C": (_C, "cardinal word"),
#         "/o": (_o, "ordinal decimal"),
#         "/O": (_O, "ordinal word"),
#     }
#     FORMAT_KEYS = list(FORMATS.keys())
#     VERBOSE_P = re.compile(r"/v(.+)")
#
#     nthalize_args = nth.nthalize.default_args()
#
#     with suppress(KeyboardInterrupt, EOFError):
#         print(loc["convert_interactive_help"])
#         print(loc["convert_interactive_help_extended"])
#         while line := input("> "):
#             match line:
#                 case "/h":
#                     print(loc["convert_interactive_help"])
#                 case s if (m := VERBOSE_P.fullmatch(s)) is not None:
#                     g = m.group(1)
#                     try:
#                         n = int(g)
#                         nth_logger.setLevel(n)
#                         print(f"log level set to {n}")
#                     except ValueError:
#                         print(f'invalid non-numeric log level "{g}"')
#                 case s if s in FORMAT_KEYS:
#                     format, msg = FORMATS[s]
#                     nthalize_args.update(format)
#                     print(f"format changed to {msg}")
#                 case _:
#                     print(_nthalize(line, nthalize_args))
#
#     readline.write_history_file(HISTORY_PATH)
#
#
# def main():
#     """Main driver function."""
#     loc: Locale = LOCALES["enUS"]
#
#     # ------------------------------------------------------------------------------------
#     # base command
#     # ------------------------------------------------------------------------------------
#     parser = argparse.ArgumentParser(
#         __name__.removesuffix(".__main__"),
#         description=loc["help"],
#         epilog=loc["help_epilog"],
#     )
#
#     parser.add_argument(
#         "-v",
#         dest="verbose",
#         action="count",
#         default=0,
#         help=loc["arg_verbose"],
#     )
#
#     subparsers = parser.add_subparsers(metavar="cmd")
#
#     # ------------------------------------------------------------------------------------
#     # detect subcommand
#     # ------------------------------------------------------------------------------------
#     detect_parser = subparsers.add_parser(
#         "detect",
#         help=loc["detect_help"],
#         description=loc["detect_description"],
#     )
#     detect_parser.set_defaults(func=_nth_detect)
#     detect_parser.add_argument(
#         "input",
#         metavar="INPUT",
#         help=loc["detect_arg_input"],
#     )
#
#     # ------------------------------------------------------------------------------------
#     # convert subcommand
#     # ------------------------------------------------------------------------------------
#     convert_parser = subparsers.add_parser(
#         "convert",
#         help=loc["convert_help"],
#         description=loc["convert_description"],
#         epilog=loc["convert_epilog"],
#     )
#     convert_parser.set_defaults(func=_nth_convert)
#     convert_mode_group = convert_parser.add_mutually_exclusive_group(required=True)
#     convert_mode_group.add_argument(
#         "-f",
#         "--format",
#         choices=["c", "C", "o", "O"],
#         help=loc["convert_arg_format"],
#     )
#     convert_mode_group.add_argument(
#         "-i",
#         "--interactive",
#         action="store_true",
#         help=loc["convert_arg_interactive"],
#     )
#
#     # ------------------------------------------------------------------------------------
#     args = parser.parse_args()
#
#     log_level = DEFAULT_LOG_LEVEL - 10 * args.verbose
#     logging.basicConfig(
#         level=log_level,
#         format="(%(pathname)s:%(lineno)d)\n%(message)s",
#     )
#
#     args.func(loc, args)
#
#
# if __name__ == "__main__":
#     main()
