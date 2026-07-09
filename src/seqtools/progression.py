import itertools as it  # pending for correct annotation
from collections.abc import Iterator
from math import log, trunc
from operator import floordiv, mul
from typing import Self

from attrs import frozen

from .bases import BaseProgression



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
            return -1
        else:
            return trunc(index)

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
            it.repeat(self.step, len(self.r) - 1), floordiv, initial=self.last
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
