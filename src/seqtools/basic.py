from __future__ import annotations

from collections import Counter, UserDict, UserList
from collections.abc import Iterator, Sequence
from functools import wraps
from itertools import chain, islice
from typing import Any, overload

from more_itertools import locate

from .bases import (
    OPINT,
    BaseIndexed,
    Ranged,
    WithData,
    boolen,
    datamethod,
    frozen_dataclass,
    slicer,
)
from .funcs import getitems


@frozen_dataclass(order=True)
class SequenceView(WithData):
    """Creates a protected view of a sequence."""

    __slots__ = ()

    @overload
    def __getitem__(self, index: int, /) -> WithData.T: ...

    @overload
    def __getitem__(self, index: slice, /) -> Slice: ...

    def __getitem__(self, index: int | slice, /) -> Slice | WithData.T:
        data = self.data
        if isinstance(index, slice):
            indices = range(len(data))[index]
            if indices.step < 0:
                return Slice(ReverseView(data), indices[::-1])
            else:
                return Slice(data, indices)
        else:
            return data[index]

    index, count = UserList.index, UserList.count

    __len__, __contains__ = UserList.__len__, UserList.__contains__

    __iter__ = UserDict.__iter__

    __reversed__, __bool__ = datamethod(reversed), datamethod(bool)

    def __repr__(self, /):
        return f"{type(self).__name__}({self.data!r})"


class ReverseView(SequenceView):
    """Creates a view that emulates the given sequence in reverse order."""

    __slots__ = ()

    __reversed__, __iter__ = SequenceView.__iter__, SequenceView.__reversed__

    def __new__(cls, data: Sequence, /):
        if isinstance(data, cls):
            return SequenceView(data.data)
        else:
            return super().__new__(cls)

    def __getitem__(self, index: int | slice, /) -> SequenceView | ReverseView | T:
        data = self.data
        if isinstance(index, slice):
            indices = range(len(data))[index]
            if indices.step < 0:
                return Slice(data, indices[::-1])
            else:
                return Slice(self, indices)
        else:
            return data[~index]

    def index(self, value: Any, start: int = 0, stop: OPINT = None, /) -> int:
        n = len(data := self.data)
        getindex = data.index
        if not start and stop is None:
            return ~getindex(value)
        else:
            return ~getindex(value, ~stop + n, ~start + n)


@frozen_dataclass
class Indexed(BaseIndexed):
    """Emulates a sequence that is the result of collect a group of indexes of
    a determined sequence."""

    def __len__(self, /):
        return len(self.r) if self.data else 0

    def __iter__(self, /):
        return getitems(self.data, self.r)

    def __reversed__(self, /):
        return getitems(self.data, reversed(self.r))

    def _getitem(self, index: int, /):
        return self.data[index]

    def _getslice(self, r: Sequence[int], /):
        return type(self)(self.data, r)

    def _index(self, obj, indices, /):
        return indices.index(self.data.index(obj))

    def _count(self, obj, indices, /):
        return sum(map(Counter(indices).get, locate(self.data, obj)))

    def unpack(self, /) -> Iterator:
        return getitems(self.data, self.r)


@frozen_dataclass
class Slice(Ranged, Indexed):
    """Emulates a slice of the given sequence.
    Example:
    >> x = Slice([1, 2, 3, 4, 5, 6, 7], 2, 5)
    >> print(x[2]) #prints 5

    Notes: Negative steps, can cause undefined behavior.
    """

    __slots__ = ()

    @slicer
    def fromindices(self, data: Sequence, slicer: slice, /):
        if isinstance(data, Slice):
            r = data.r[slicer]
        else:
            r = range(*slicer.indices(len(data)))

        super().__init__(data, r)

    def __reversed__(self, /):
        size = len(data := self.data)
        if start := (r := self.r).start:
            return getitems(data, r)
        return islice(
            chain((None,), reversed(data)),
            size - start,
            size - self.stop,
            abs(self.step),
        )

    def __iter__(self, /):
        gen = iter(data := self.data)
        r = self.r
        stop, step = r.stop, r.step
        if start := r.start:
            try:
                gen.__setstate__(start)
            except AttributeError:
                return getitems(data, r)
            else:
                stop -= start
                start = 0
        return islice(gen, start, stop, step)

    def _contains(self, value, indices, /):
        try:
            return self.data.index(value, indices.start, indices.stop) in indices
        except ValueError:
            pass
        except TypeError:
            return value in iter(self)

    # bool and integer functions decorator

    @boolen
    def __bool__(data, r, /):
        return start < min(len(data), r.stop) if (start := r.start) else True

    @boolen
    def __len__(data, r, /):
        value = min(len(data), r.stop) - r.start
        return -(-value // r.step) if value > 0 else 0


    def __eq__(self, value, /):
        return (
            type(self) is type(value) and self.data is value.data and self.r == value.r
        )

    def _index(self, value, r, /) -> int:
        if r:
            data = self.data
            index = data.index
            start = r.start
            stop = r.stop
            return r.index(
                index(value) if not (start or stop) else index(value, start, stop)
            )
        self.value_error(value)

    # peging
    def count(self, value, indices, /) -> int:
        if indices:
            try:
                return self.data.count(value, indices.start, indices.stop)
            except TypeError:
                return super().count(value)
        return 0

    def unpack(self, /) -> Iterator[Any]
        return self.data[(r := self.r).start : r.stop : r.step]
