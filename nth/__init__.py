"""Nth, utility for converting number formats within strings."""
import logging
import os

from . import nthalize

logger = logging.getLogger(__name__)
if (log_level_str := os.environ.get("NTH_LEVEL")) is not None:
    if log_level_str.isdecimal():
        log_level = int(log_level_str)
    else:
        log_level = logging.getLevelName(log_level_str)
    logger.setLevel(log_level)


_nthalize = nthalize.nthalize
NthalizeArgs = nthalize.NthalizeArgs
WordBehavior = nthalize.WordBehavior


def _args(as_word: bool, number_kind: nthalize.NumberKind):
    return NthalizeArgs(
        number=number_kind,
        format="WORD" if as_word else "DECIMAL",
        word_behavior=nthalize.default_word_behavior(),
    )


def cardinalize(s: str, as_word: bool = False):
    """Convert numbers within a string to cardinal formal."""
    return _nthalize(s, _args(as_word, "CARDINAL"))


def ordinalize(s: str, as_word: bool = False):
    """Convert numbers within a string to ordinal formal."""
    return _nthalize(s, _args(as_word, "ORDINAL"))
