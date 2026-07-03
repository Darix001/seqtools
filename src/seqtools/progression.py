import itertools as it
import math
import operator as op
from abc import abstractmethod
from collections.abc import Iterator, Sequence
from decimal import Decimal
from fractions import Fraction
from numbers import Integral, Real
from typing import Self, TypeVar

from attrs import field, frozen

from .bases import Ranged, pos_range

T = TypeVar("T", int, float, Decimal, Fraction, Real, Integral)


@frozen(slots=True)
class BaseProgression[T](Ranged[T]):
    a1: T
    data: Sequence[T] = field(init=False, repr=False)

    @abstractmethod
    def unbound_index(self, number: T) -> int: ...

    @abstractmethod
    def _sliced(self, r: range, /) -> Self: ...

    def _contains(self, number, /):
        return self.unbound_index(number) in self.r

    @property
    def an(self, /) -> T:
        return self._getitem(self.r[-1])

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


@frozen(order=True, slots=True)
class ArithmeticProgression[T](BaseProgression[T]):
    """Emulates an Arithmetic Progression:
    r = A range indicating the indices of the progression.
    a1 = the first term of the progression.
    d = teh distance between each term.

    Example:
    >>P = Progression.sized(.1, .1, n=10)
    >>P[2] #prints .3


    """

    distance: T
    r: range = field(converter=pos_range)

    def _sliced(self, r, /) -> Self:
        return type(self)(self._getitem(r.start), r.step * self.distance, len(r))

    def _getitem(self, index: int, /) -> T:
        return self.a1 + (index * self.distance)

    def unbound_index(self, number: T, /) -> int:
        if (index := (number - self.a1) / self.distance) % 1:
            return math.trunc(index)
        else:
            return -1

    def __iter__(self, /) -> Iterator[T]:
        return it.islice(it.count(self.a1, self.distance), len(self))

    def __reversed__(self, /) -> Iterator[T]:
        return it.islice(it.count(self.an, -self.distance), len(self))

    @classmethod
    def fromrange(cls, rng: range, /):
        """Create Progression from a range. The stop argument will not be
        preserved if (stop - last_range_number) != step"""

        return cls(len(rng), rng.start, rng.step)


@frozen(order=True, slots=True)
class GeometricProgression[T](BaseProgression[T]):
    ratio: T
    r: range = field(converter=pos_range)

    def _getitem(self, index: int, /) -> T:
        return self.a1 * self.ratio**index

    def _sliced(self, r: range, /) -> Self:
        ratio = self.ratio * abs(r.step)
        if r.step < 0:
            ratio = 1 / ratio
        return type(self)(self._getitem(r.start), ratio, len(r))

    def __iter__(self, /) -> Iterator[T]:
        return it.accumulate(
            it.repeat(self.ratio, len(self.r) - 1), op.mul, initial=self.a1
        )

    def __reversed__(self, /) -> Iterator[T]:
        return it.accumulate(
            it.repeat(self.ratio, len(self.r) - 1), op.floordiv, initial=self.an
        )

    def unbound_index(self, number: T, /) -> int:
        if (index := math.log(number / self.a1, self.ratio)).is_integer():
            return math.trunc(index)
        else:
            return -1

    def index(self, number: T, /) -> int:
        return self.r.index(self.unbound_index(number))

    def sum(self, /) -> T:
        return (self.a1 * (1 - self.ratio ** len(self))) / (1 - self.ratio)


if __name__ == "__main__":
    import builtins

    geoprog = GeometricProgression(2, 2, 10)
    a = geoprog[1]
    test_list = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    assert test_list == list(geoprog)
    assert test_list[::-1] == list(reversed(geoprog))
    assert test_list[-3] == geoprog[-3]
    assert test_list[5] == geoprog[5]
    assert test_list.index(128) == geoprog.index(128)
    assert test_list.count(128) == geoprog.count(128)
    assert builtins.sum(geoprog) == geoprog.sum()
