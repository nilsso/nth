import typing
from contextlib import suppress

_T1 = typing.TypeVar("_T1")
_T2 = typing.TypeVar("_T2")


def intersperse(  # noqa
    iterable: typing.Iterable[_T1],
    fill: _T2,
) -> typing.Iterator[_T1 | _T2]:
    it = iter(iterable)
    with suppress(StopIteration):
        yield next(it)
        for v in it:
            yield fill
            yield v
