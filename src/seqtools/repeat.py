from collections.abc import Iterator
from itertools import repeat
from operator import attrgetter
from typing import Any, Self, TypeVar

from attrs import field, frozen

from .bases import OPINT, Ranged, RelativeSized, Sequence, WithData
from .funcs import from_iterable, map_repeat, reverse_all

div_index = {0, -1}.__contains__


V = TypeVar("V")


@frozen
class Repeat[V](Ranged):
    """Same as it.repeat but as a sequence."""

    data: V
    r: range = field(
        converter=lambda r: range(0 if r < 0 else r), repr=attrgetter("stop")
    )

    def __len__(self, /) -> int:
        return self.r.stop

    def __iter__(self, /) -> Iterator[V]:
        return repeat(self.data, self.r.stop)

    __reversed__ = __iter__

    def _contains(self, obj: Any, r: range, /):
        return self.data == obj

    def __add__(self, value, /):
        if isinstance(value, cls := type(self)):
            if (v := self.data) == value.value:
                return cls(v, self.r.stop + value.r.stop)
        return NotImplemented

    def _getitem(self, index: int, /) -> V:
        return self.data

    def _getslice(self, r: range, /) -> Self:
        return type(self)(self.data, self.r.stop)

    def _count(self, value: Any, r: range, /) -> int:
        return +(self.data == value)

    def _index(self, value: Any, r: range, /) -> int:
        if self.data == value:
            return 0
        else:
            raise self.value_error(value)

    def tolist(self, /) -> list[V]:
        return [self.data] * self.r.stop

    def to_tuple(self, /) -> tuple[V, ...]:
        return (self.data,) * self.r.stop


@frozen
class Mul(RelativeSized):
    """Emulates a data sequence repeated r times.
    Example:
        a = Mul(range(2), 3)
        print(*a)
        #prints 0 1 0 1 0 1
    """

    r: int
    __slots__ = ()

    def __new__(cls, data: Sequence[WithData.T], r: int):
        if isinstance(data, cls):
            r *= data.r
            data = data.data
        return super().__new__(cls, data, r)

    def __mul__(self, r, /):
        return self._replace(r=self.r * r)

    def __add__(self, value, /):
        if type(self) is type(value):
            if (data := self.data) == data.data:
                return self._replace(r=self.r + data.r)
        return NotImplemented

    def __getitem__(self, index, /):
        try:
            floordiv, index = divmod(index, len(data := self.data))
            if div_index(floordiv // self.r):
                return data[index]
        except ZeroDivisionError:
            pass
        raise self.index_error()

    def __len__(self, /):
        return len(self.data) * self.r

    def __contains__(self, value, /):
        return True if self.r and (value in self.data) else False

    def __iter__(self, /) -> Iterator[WithData.T]:
        return from_iterable(repeat(self.data, self.r))

    def __reversed__(self, /) -> Iterator[WithData.T]:
        return from_iterable(reverse_all(repeat(self.data, self.r)))

    def count(self, value, /) -> int:
        return (r := self.r) and self.data.count(value) * r

    def index(self, value, start=0, stop: OPINT = None, /) -> int:
        index = self.data.index
        if r := self.r:
            if stop is None and not start:
                return index(value)
            div, start = divmod(start, r)
            if div_index(div):
                return index(value, start, stop % r if stop else r)
        raise self.data_error(value)

    def unpack(self, /) -> Sequence:
        return self.data * self.r


@frozen
class Repeats(Mul):
    """Emulates a sequence with each elements repeated r times."""

    __slots__ = ()

    def __mul__(self, n, /):
        return Mul(self, n)

    def __getitem__(self, index, /):
        if r := self.r:
            return self.data[index // r]
        else:
            raise self.index_error()

    def iterfunc(reverse, /):
        def __iter__(self, /):
            data = self.data
            if reverse:
                data = reversed(data)
            return from_iterable(map_repeat(data, repeat(self.r)))

        return __iter__

    def index(self, value, start=0, stop: OPINT = None, /) -> int:
        if not (r := self.r):
            raise self.data_error(value)

        index = self.data.index

        if stop is None and not start:
            return index(value) * r

        start, mod = divmod(start, r)
        return (index(value, start, stop // r) * r) + mod
