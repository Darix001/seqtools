import itertools as it
import math
import operator as op
from abc import abstractmethod
from collections.abc import Iterator, Sequence
from dataclasses import dataclass, field
from functools import partial
from numbers import Number
from typing import Self

from .bases import Ranged, WithData, frozen_dataclass, slicer
from .funcs import check_step

frozen_slotted_dt = partial(frozen_dataclass, slots=True)

# PENDING: Reverse and Negative indices are not supported


@frozen_slotted_dt
class BaseProgression(Ranged, Sequence[Number]):
    a1: Number
    data: Sequence[WithData.T] = field(init=False, repr=False)

    @abstractmethod
    def _unbound_index(self, number: Number) -> float | int: ...

    @abstractmethod
    def _sliced(self, r: range) -> Self: ...

    def _contains(self, number, /):
        return self._unbound_index(number) in self.r

    def __len__(self, /):
        return len(self.r)

    def __bool__(self, /):
        return bool(self.r)

    @property
    def an(self, /) -> Number:
        return self._getitem(self.r[-1])

    def clear(self, /) -> Self:
        return type(self)(range(0), 0, 0)

    def _getslice(self, r: range) -> Self:
        if r:
            return self._sliced(r)
        else:
            return self.clear()

    def _count(self, number: Number, r: range, /) -> int:
        return r.count(self._unbound_index(number))

    def _index(self, number: Number, r: range, /) -> int:
        return r.index(self._unbound_index(number))


@frozen_slotted_dt(order=True)
class ArithmeticProgression(BaseProgression):
    """Emulates an Arithmetic Progression:
    r = A range indicating the indices of the progression.
    a1 = the first term of the progression.
    d = teh distance between each term.

    Example:
    >>P = Progression.sized(.1, .1, n=10)
    >>P[2] #prints .3


    """

    distance: Number

    def _sliced(self, r, /) -> Self:
        return type(self)(range(len(r)), self._getitem(r.start), r.step * self.distance)

    def _getitem(self, index: int, /) -> Number:
        return self.a1 + (index * self.distance)

    def _unbound_index(self, number: Number, /) -> Number:
        return (number - self.a1) / self.distance

    def __iter__(self, /) -> Iterator[Number]:
        return it.islice(it.count(self.a1, self.distance), self.r.stop)

    def __reversed__(self, /) -> Iterator[Number]:
        return it.islice(it.count(self.an, -self.distance), self.r.stop)

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

    @classmethod
    def sized(cls, /, a1: Number, distance: Number, n: int):
        """Returns a Progression form start with step of size n"""
        if n < 0:
            raise ValueError("size must be non-negative")
        return cls(range(n), a1, distance)


@frozen_slotted_dt(order=True)
class GeometricProgression(BaseProgression):
    ratio: Number

    def _getitem(self, index: int, /):
        return self.a1 * self.ratio**index

    def _sliced(self, r: range) -> Self:
        ratio = self.ratio * abs(r.step)
        if r.step < 0:
            ratio = 1 / ratio
        return type(self)(range(len(r)), self._getitem(r.start), ratio)

    def __iter__(self, /) -> Iterator[Number]:
        return it.accumulate(
            it.repeat(self.ratio, len(self.r) - 1), op.mul, initial=self.a1
        )

    def __reversed__(self, /) -> Iterator[Number]:
        return it.accumulate(
            it.repeat(self.ratio, len(self.r) - 1), op.floordiv, initial=self.an
        )

    def _unbound_index(self, number: Number, /) -> float | int:
        return math.log(number / self.a1, self.r)

    def index(self, number: Number, /) -> int:
        return self.r.index(self._unbound_index(number))

    def sum(self, /) -> Number:
        return (self.start * (1 - self.r**self.n)) / (1 - self.r)

    @classmethod
    def sized(cls, /, a1: Number, ratio: Number, n: int):
        """Returns a Progression form start with step of size n"""
        if n < 0:
            raise ValueError("size must be non-negative")
        return cls(range(n), a1, ratio)


if __name__ == "__main__":
    import builtins

    geoprog = GeometricProgression(2, 2, 10)
    test_list = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    assert test_list == list(geoprog)
    assert test_list[::-1] == list(reversed(geoprog))
    assert test_list[-3] == geoprog[-3]
    assert test_list[5] == geoprog[5]
    assert test_list.index(128) == geoprog.index(128)
    assert test_list.count(128) == geoprog.count(128)
    assert builtins.sum(geoprog) == geoprog.sum()
