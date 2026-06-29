from collections.abc import Iterator
from dataclasses import field
from functools import partial
from itertools import chain, islice, repeat, zip_longest
from operator import indexOf, itemgetter, sub
from typing import Any, Generic, Self, TypeVar, Unpack, overload

from .bases import (
    NS,
    TVT,
    Sequence,
    SubSequence,
    calcsize,
    datamethod,
    frozen_dataclass,
    get_sizes,
)
from .basic import Slice
from .funcs import get


@frozen_dataclass
class BaseZip(SubSequence, Generic[Unpack[TVT]]):
    __slots__ = ()

    data: tuple[Unpack[TVT]]

    def _levels(self, /) -> Iterator[tuple[Sequence, int]]:
        data = self.data
        n = repeat(len(self))
        return zip(data, map(abs, map(sub, n, get_sizes(data))))


@frozen_dataclass(slots=True)
class Zip(BaseZip):
    """Same as builtins.zip but as a sequence."""

    strict: bool = field(kw_only=True, default=False)

    def __bool__(self, /) -> bool:
        return True if (data := self.data) and all(data) else False

    __len__ = calcsize(min)

    @overload
    def __getitem__(self, index: Any, /) -> tuple[Any]: ...

    @overload
    def __getitem__(self, index: slice, /) -> Self: ...

    def __getitem__(self, index: Any | slice, /):
        data = self.data

        if isinstance(index, slice):
            return type(self)(*map(partial(Slice.fromindices, slice_obj=index), data))
        else:
            return tuple(map(itemgetter(index), data))

    def __iter__(self, /) -> Iterator[tuple[Any]]:
        return zip(*self.data, strict=self.strict)

    def __reversed__(self, /) -> Iterator[tuple[Any]]:
        return zip(*self._reversegen(self._levels(), self.strict))

    @staticmethod
    def _reversegen(levels, r, /) -> Iterator[tuple[Any]]:
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

    @classmethod
    def unzip(cls, data: NS, strict: bool = False) -> Self:
        (new := cls(strict=strict))._setattr("data", data)
        return new


@frozen_dataclass
class ZipLongest(BaseZip):
    """Same as it.zip_longest but as a sequence."""

    fillvalue: Any = field(kw_only=True, default=None)

    datamethod(any)

    __len__ = calcsize(max)

    @overload
    def __getitem__(self, index: slice, /) -> Self: ...

    @overload
    def __getitem__(self, index: int, /) -> tuple[Any]: ...

    def __getitem__(self, index, /):
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

    def __iter__(self, /):
        return zip_longest(*self.data, fillvalue=self.fillvalue)

    @staticmethod
    def _reversegen(levels, default, /):
        for data, level in levels:
            data = reversed(data)
            if level:
                data = chain(repeat(default, level), data)
            yield data

    @classmethod
    def unzip(cls, data: NS, fillvalue: Any = None):
        (new := cls(fillvalue=fillvalue))._setattr("data", data)
        return new


del Iterator
