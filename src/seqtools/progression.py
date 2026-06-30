import itertools as it
import math
import operator as op
from abc import abstractmethod
from collections.abc import Iterator, Sequence
from decimal import Decimal
from fractions import Fraction
from numbers import Integral, Real
from typing import Generic, Self, TypeVar

from attrs import field, frozen

from .bases import Ranged, WithData, slicer
from .funcs import check_step

# PENDING: Reverse and Negative indices are not supported

T = TypeVar("T", int, float, Decimal, Fraction, Real, Integral)


@frozen(slots=True)
class BaseProgression(Ranged, Generic[T]):
    a1: T
    data: Sequence[WithData.T] = field(init=False, repr=False)

    @abstractmethod
    def _unbound_index(self, number: T) -> float | int: ...

    @abstractmethod
    def _sliced(self, r: range) -> Self: ...

    def _contains(self, number, /):
        return self._unbound_index(number) in self.r

    def __len__(self, /):
        return len(self.r)

    def __bool__(self, /):
        return bool(self.r)

    @property
    def an(self, /) -> T:
        return self._getitem(self.r[-1])

    def clear(self, /) -> Self:
        return type(self)(range(0), 0, 0)

    def _getslice(self, r: range) -> Self:
        if r:
            return self._sliced(r)
        else:
            return self.clear()

    def _count(self, number: T, r: range, /) -> int:
        return r.count(self._unbound_index(number))

    def _index(self, number: T, r: range, /) -> int:
        return r.index(self._unbound_index(number))


@frozen(order=True, slots=True)
class ArithmeticProgression(BaseProgression):
    """Emulates an Arithmetic Progression:
    r = A range indicating the indices of the progression.
    a1 = the first term of the progression.
    d = teh distance between each term.

    Example:
    >>P = Progression.sized(.1, .1, n=10)
    >>P[2] #prints .3


    """

    distance: T

    def _sliced(self, r, /) -> Self:
        return type(self)(range(len(r)), self._getitem(r.start), r.step * self.distance)

    def _getitem(self, index: int, /) -> T:
        return self.a1 + (index * self.distance)

    def _unbound_index(self, number: T, /) -> T:
        return (number - self.a1) / self.distance

    def __iter__(self, /) -> Iterator[T]:
        return it.islice(it.count(self.a1, self.distance), len(self))

    def __reversed__(self, /) -> Iterator[T]:
        return it.islice(it.count(self.an, -self.distance), len(self))

    @classmethod
    @slicer
    def fromrange(cls, slicer, /):
        """Create Progression from a range. The stop argument will not be
        preserved if (stop - last_range_number) != step"""
        if (step := slicer.step) is None:
            growing = step = 1

        else:
            check_step(step)
            growing = step > 0

        stop = slicer.stop

        if (start := slicer.start) is None:
            start = 1
            n = math.trunc(slicer.stop)

        elif (start == stop) or (growing and start > stop) or (start < stop):
            n = 0

        else:
            diff = stop - start if growing else start - stop
            n = math.ceil(diff / abs(step))

        return cls(range(n), start, step)


@frozen(order=True, slots=True)
class GeometricProgression(BaseProgression):
    ratio: T

    def _getitem(self, index: int, /) -> T:
        return self.a1 * self.ratio**index

    def _sliced(self, r: range) -> Self:
        ratio = self.ratio * abs(r.step)
        if r.step < 0:
            ratio = 1 / ratio
        return type(self)(range(len(r)), self._getitem(r.start), ratio)

    def __iter__(self, /) -> Iterator[T]:
        return it.accumulate(
            it.repeat(self.ratio, len(self.r) - 1), op.mul, initial=self.a1
        )

    def __reversed__(self, /) -> Iterator[T]:
        return it.accumulate(
            it.repeat(self.ratio, len(self.r) - 1), op.floordiv, initial=self.an
        )

    def _unbound_index(self, number: T, /) -> float | int:
        return math.log(number / self.a1, self.ratio)

    def index(self, number: T, /) -> int:
        return self.r.index(self._unbound_index(number))

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
