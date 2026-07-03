import itertools as it  # pending for correct annotation
from abc import abstractmethod
from collections.abc import Iterator, Sequence
from math import log, trunc
from operator import floordiv, mul
from typing import Self

from attrs import field, frozen

from .bases import Ranged, pos_range


@frozen(slots=True)
class BaseProgression[T](Ranged[T]):
    start: T
    step: T
    r: range = field(converter=pos_range, alias="size")
    data: Sequence[T] = field(init=False, repr=False)

    def __repr__(self, /) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.step!r}, size={len(self.r)!r})"

    @abstractmethod
    def unbound_index(self, number: T) -> int: ...

    @abstractmethod
    def _sliced(self, r: range, /) -> Self: ...

    def _contains(self, number, /):
        return self.unbound_index(number) in self.r

    @property
    def stop(self, /) -> T:
        return self._getitem(self.r.stop)

    def clear(self, /) -> Self:
        return type(self)(0, 0, 0)

    def _getslice(self, r: range, /) -> Self:
        if r:
            return self._sliced(r)
        else:
            return self.clear()

    def _count(self, number: T, r: range, /) -> int:
        return r.count(self.unbound_index(number))

    def _index(self, number: T, r: range, /) -> int:
        return r.index(self.unbound_index(number))


@frozen(order=True, repr=False)
class ArithmeticProgression[T](BaseProgression[T]):
    """Emulates stop Arithmetic Progression:
    r = A range indicating the indices of the progression.
    start = the first term of the progression.
    d = teh distance between each term.

    Example:
    >>P = Progression(10, .1, .1)
    >>P[2] #prints .3


    """

    __slots__ = ()

    def _sliced(self, r, /) -> Self:
        return type(self)(self._getitem(r.start), r.step * self.step, len(r))

    def _getitem(self, index: int, /) -> T:
        return self.start + (index * self.step)

    def unbound_index(self, number: T, /) -> int:
        if (index := (number - self.start) / self.step) % 1:
            return trunc(index)
        else:
            return -1

    def __iter__(self, /) -> Iterator[T]:
        return it.islice(it.count(self.start, self.step), len(self))

    def __reversed__(self, /) -> Iterator[T]:
        return it.islice(it.count(self.stop, -self.step), len(self))

    @classmethod
    def fromrange(cls, rng: range, /):
        """Create Progression from a range. The stop argument will not be
        preserved if (stop - last_range_number) != step"""

        return cls(len(rng), rng.start, rng.step)


@frozen(order=True, repr=False)
class GeometricProgression[T](BaseProgression[T]):
    __slots__ = ()

    def _getitem(self, index: int, /) -> T:
        return self.start * self.step**index

    def _sliced(self, r: range, /) -> Self:
        ratio = self.step * abs(r.step)
        if r.step < 0:
            ratio = 1 / ratio
        return type(self)(self._getitem(r.start), ratio, len(r))

    def __iter__(self, /) -> Iterator[T]:
        return it.accumulate(
            it.repeat(self.step, len(self.r) - 1), mul, initial=self.start
        )

    def __reversed__(self, /) -> Iterator[T]:
        return it.accumulate(
            it.repeat(self.step, len(self.r) - 1), floordiv, initial=self.stop
        )

    def unbound_index(self, number: T, /) -> int:
        if (index := log(number / self.start, self.step)).is_integer():
            return trunc(index)
        else:
            return -1

    def index(self, number: T, /) -> int:
        return self.r.index(self.unbound_index(number))

    def sum(self, /) -> T:
        return (self.start * (1 - self.step ** len(self))) / (1 - self.step)


if __name__ == "__main__":
    import builtins

    geoprog = GeometricProgression[int](start=2, step=2, size=10)
    a = geoprog[1]
    test_list = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    assert test_list == list(geoprog)
    assert test_list[::-1] == list(reversed(geoprog))
    assert test_list[-3] == geoprog[-3]
    assert test_list[5] == geoprog[5]
    assert test_list.index(128) == geoprog.index(128)
    assert test_list.count(128) == geoprog.count(128)
    assert builtins.sum(geoprog) == geoprog.sum()
