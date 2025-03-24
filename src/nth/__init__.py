"""Nth, utility for converting number formats within strings."""

import logging

from . import nthalize as nthalize

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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
