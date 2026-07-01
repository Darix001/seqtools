from __future__ import annotations

import operator as op
from collections import Counter, UserList
from collections.abc import Iterator, Sequence
from itertools import chain, islice
from typing import Any, Generic, Self, TypeVar, overload

from attrs import field, frozen
from more_itertools import locate

from .bases import (
    OPINT,
    BaseIndexed,
    Ranged,
    WithData,
    boolen,
    slicer,
)
from .funcs import getitems


@frozen(order=True, repr=False)
class SequenceView[T](WithData[T]):
    """Creates a protected view of a sequence."""

    data: Sequence[T]

    __slots__ = ()

    @overload
    def __getitem__(self, index: int, /) -> T: ...

    @overload
    def __getitem__(self, index: slice, /) -> Slice: ...

    def __getitem__(self, index: int | slice, /) -> Slice | T:
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

    def __iter__(self, /) -> Iterator[T]:
        return iter(self.data)

    def __reversed__(self, /) -> Iterator[T]:
        return reversed(self.data)

    def __bool__(self, /) -> bool:
        return bool(self.data)


class ReverseView[T](SequenceView[T]):
    """Creates a view that emulates the given sequence in reverse order."""

    __slots__ = ()

    __reversed__, __iter__ = SequenceView.__iter__, SequenceView.__reversed__

    def __new__(cls, data: Sequence, /):
        if isinstance(data, cls):
            return SequenceView(data.data)
        else:
            return super().__new__(cls)

    @overload
    def __getitem__(self, index: int, /) -> T: ...

    @overload
    def __getitem__(self, index: slice, /) -> Slice: ...

    def __getitem__(self, index: int | slice, /) -> Slice | T:
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
        if not start and stop is None:
            return ~data.index(value)
        else:
            return ~data.index(value, ~stop + n if stop else n, ~start + n)


@frozen
class Indexed[T](BaseIndexed[T]):
    """Emulates a sequence that is the result of collect a group of indexes of
    a determined sequence."""

    r: Sequence[int] = field(alias="indices")

    __slots__ = ()

    def __len__(self, /) -> int:
        return len(self.r) if self.data else 0

    def __iter__(self, /) -> Iterator[T]:
        return getitems(self.data, self.r)

    def __reversed__(self, /) -> Iterator[T]:
        return getitems(self.data, reversed(self.r))

    def _getitem(self, index: int, /) -> T:
        return self.data[index]

    def _getslice(self, r: Sequence[int], /):
        return type(self)(self.data, r)

    def _index(self, obj, indices, /):
        return indices.index(self.data.index(obj))

    def _count(self, obj, indices, /):
        return sum(map(Counter(indices).get, locate(self.data, obj)))

    def unpack(self, /) -> Sequence[T]:
        r = self.r
        return self.data[r.start : r.stop : r.step]


@frozen
class Slice[T](Ranged[T], Indexed[T]):
    """Emulates a slice of the given sequence.
    Example:
    >> x = Slice.fromindices([1, 2, 3, 4, 5, 6, 7], 2, 5)
    >> print(x[2]) #prints 5

    """

    __slots__ = ()
    r: range = field(converter=None)

    @classmethod
    @slicer
    def fromindices(cls, data: Sequence[T], slice_obj: slice, /) -> Self:
        if isinstance(data, Slice):
            r = data.r[slice_obj]
        else:
            r = range(*slice_obj.indices(len(data)))

        return cls(data, r)

    def __reversed__(self, /) -> Iterator[T]:
        size = len(data := self.data)
        if start := (r := self.r).start or (step := r.step) < 0:
            return getitems(data, r)
        return islice(
            chain((None,), reversed(data)),
            size - start,
            size - r.stop,
            step,
        )

    def __iter__(self, /) -> Iterator[T]:
        r = self.r
        data = self.data
        stop, step = r.stop, r.step
        if step < 0:
            return getitems(data, r)
        gen = iter(data)
        if start := r.start:
            try:
                gen.__setstate__(start)
            except AttributeError:
                return getitems(data, r)
            else:
                stop -= start
                start = 0
        return islice(gen, start, stop, step)

    def _contains(self, value, indices, /) -> bool:
        try:
            return self.data.index(value, indices.start, indices.stop) in indices
        except ValueError:
            return False
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
        raise self.value_error(value)

    def _count(self, value, r: range, /) -> int:
        return op.countOf(type(self)(self.data, r), value)

    def unpack(self, /) -> Sequence[T]:
        return self.data[(r := self.r).start : r.stop : r.step]
