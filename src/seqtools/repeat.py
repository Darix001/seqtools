from collections.abc import Iterator
from itertools import repeat
from typing import Any, Self, TypeVar

from .bases import OPINT, Ranged, RelativeSized, Sequence, WithData, frozen_dataclass
from .funcs import from_iterable, map_repeat, reverse_all

div_index = {0, -1}.__contains__


V = TypeVar("V")


@frozen_dataclass
class Repeat[V](Ranged):
    """Same as it.repeat but as a sequence."""

    value: V

    def __init__(self, /, object: Any, times: int):
        super().__init__(range(times >= 0 and times))
        self._setattr("value", object)

    def __len__(self, /) -> int:
        return self.r.stop

    def __iter__(self, /) -> Iterator[V]:
        return repeat(self.value, self.r.stop)

    __reversed__ = __iter__

    def __contains__(self, obj: Any, /):
        return True if self.r.stop and self.value == obj else False

    def __add__(self, value, /):
        if isinstance(value, cls := type(self)):
            if (v := self.value) == value.value:
                return cls(v, self.r.stop + value.r.stop)
        return NotImplemented

    def _getitem(self, index: int, /) -> V:
        return self.value

    def _getslice(self, r: range, /) -> Self:
        return type(self)(self.value, len(r))

    def count(self, value: Any, /) -> int:
        return self.r.stop if value in self else 0

    def index(self, value: Any, /) -> int:
        if value in self:
            return 0
        else:
            raise self.value_error(value)

    def tolist(self, /) -> list:
        return [self.value] * self.r.stop


@frozen_dataclass
class Mul(RelativeSized):
    """Emulates a data sequence repeated r times.
    Example:
        a = Mul(range(2), 3)
        print(*a)
        #prints 0 1 0 1 0 1
    """

    __slots__ = ()

    def __init__(self, data: Sequence, r: int, /):
        if isinstance(data, type(self)):
            r *= data.r
            data = data.data
        return super().__init__(data, r)

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
        raise self.value_error(value)

    def unpack(self, /) -> Sequence:
        return self.data * self.r


@frozen_dataclass
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
            raise self.value_error(value)

        index = self.data.index

        if stop is None and not start:
            return index(value) * r

        start, mod = divmod(start, r)
        return (index(value, start, stop // r) * r) + mod
