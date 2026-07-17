from collections.abc import Iterator
from dataclasses import field
from functools import partial
from itertools import chain, islice, repeat, zip_longest
from operator import indexOf, itemgetter, sub
from typing import Any, Generic, Self, TypeVar, TypeVarTuple, Unpack, overload

from attrs import frozen

from .bases import (
    Sequence,
    SubSequence,
    base_frozen,
    calcsize,
    datamethod,
    isizes,
)
from .basic import Slice
from .funcs import get

BZipTs = TypeVarTuple("BZipTs")
T = TypeVar("T")


@base_frozen(hash=False, eq=False)
class BaseZip(SubSequence, Generic[Unpack[BZipTs]]):
    __slots__ = ()

    data: tuple[Unpack[BZipTs]]

    def _levels(self, /) -> Iterator[tuple[Sequence, int]]:
        data = self.data
        n = repeat(len(self))
        return zip(data, map(abs, map(sub, n, isizes(data))))

    def _incomplete_repr(self, /) -> str:
        return f"{type(self).__name__}{self.data}"[:-1]


TZip = TypeVarTuple("TZip")


@frozen(slots=True, repr=True, order=True)
class Zip(BaseZip[*TZip]):
    """Same as builtins.zip but as a sequence."""

    strict: bool = field(kw_only=True, default=False)

    def __init__(self, *data: tuple[Sequence[Any]], strict: bool = False):
        self._setattr("data", data)
        self._setattr("strict", strict)

    def __repr__(self, /):
        return f"{self._incomplete_repr()}, strict={self.strict!r})"

    def __bool__(self, /) -> bool:
        return True if (data := self.data) and all(data) else False

    __len__ = calcsize(min)

    @overload
    def __getitem__(self, index: Any, /) -> tuple[*TZip]: ...

    @overload
    def __getitem__(self, index: slice, /) -> Self: ...

    def __getitem__(self, index: Any | slice, /) -> Self | tuple[*TZip]:
        data = self.data

        if isinstance(index, slice):
            return type(self)(*map(partial(Slice.fromindices, slice_obj=index), data))
        else:
            return tuple(map(itemgetter(index), data))

    def __iter__(self, /) -> Iterator[tuple[*TZip]]:
        return zip(*self.data, strict=self.strict)

    def __reversed__(self, /) -> Iterator[tuple[*TZip]]:
        return zip(*self._reversegen(self._levels(), self.strict))

    @staticmethod
    def _reversegen(levels, r, /) -> Iterator[tuple[*TZip]]:
        for i, (data, level) in enumerate(levels):
            data = reversed(data)
            if level:
                if r:
                    raise TypeError(f"Sequence #{i} has different size.")
                data = islice(data, level, None)
            yield data

    _contains = Sequence.__contains__
    _count = Sequence.count

    def _check(self, value, /) -> bool:
        return type(value) is tuple and len(value) == len(self.data)

    def _index(self, values, start, stop, /) -> int:
        if data := self.data:
            if start is not None:
                indices = [
                    seq.index(value, start, stop) for value, seq in zip(values, data)
                ]

            else:
                indices = [*map(indexOf, data, values)]

            maxvalue = max(indices)
            stop = maxvalue + 1
            n = len(data)

            while indices.count(maxvalue) != n:
                iterable = enumerate(zip(data, values, indices))

                for index, (seq, value, start) in iterable:
                    if start != maxvalue:
                        indices[index] = seq.index(value, start + 1, stop)

            return maxvalue

        raise self.value_error(values)


TZipL = TypeVarTuple("TZipL")


@frozen(slots=True, repr=False, order=True)
class ZipLongest(BaseZip[*TZip]):
    """Same as it.zip_longest but as a sequence."""

    fillvalue: Any = field(kw_only=True, default=None)

    def __init__(self, *data: tuple[Sequence[Any]], fillvalue: Any = None):
        self._setattr("data", data)
        self._setattr("fillvalue", fillvalue)

    def __repr__(self, /):
        return f"{self._incomplete_repr()}, strict={self.strict!r})"

    __bool__ = datamethod(any)

    __len__ = calcsize(max)

    @overload
    def __getitem__(self, index: slice, /) -> Self: ...

    @overload
    def __getitem__(self, index: int, /) -> tuple[*TZipL]: ...

    def __getitem__(self, index, /) -> Self | tuple[*TZipL]:
        data = self.data
        if isinstance(index, slice):
            return type(self)(*map(partial(Slice.fromindices, slice_obj=index), data))
        else:
            if index < 0:
                index += len(self)
            default = self.fillvalue
            return tuple(
                get(data, index, default) if level else data[index]
                for data, level in self._levels()
            )

    def __iter__(self, /) -> Iterator[tuple[*TZipL]]:
        return zip_longest(*self.data, fillvalue=self.fillvalue)

    @staticmethod
    def _reversegen(levels, default, /) -> Iterator[tuple[*TZipL]]:
        for data, level in levels:
            data = reversed(data)
            if level:
                data = chain(repeat(default, level), data)
            yield data


del Iterator
