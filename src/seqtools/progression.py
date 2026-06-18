import itertools as it
import math
import operator as op
from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from numbers import Number

from .bases import Ranged, frozen_dataclass, slicer
from .funcs import check_step


@frozen_dataclass(slots=True)
class Progression(Ranged):
    """Emulates an Arithmetic Progression:
    r = Arange indicating the indices of the progression.
    a1 = the first term of the progression.
    d = teh distance between each term.

    Example:
    >>P = Progression.sized(.1, .1, n=10)
    >>P[2] #prints .3
    """

    a1: Number = 0
    d: Number = 1

    def __contains__(self, number, /):
        return self._getindex(number) in self.r

    def rfunc(func, /):
        return lambda self, /: func(self.r)

    __len__, __bool__ = rfunc(len), rfunc(bool)

    del rfunc

    def _getslice(self, r, /):
        (new := type(self)(self)._setattr(1, self.d, n=0), "r", r)
        return new

    def _getitem(self, index: int, /):
        return self.a1 + (index * self.d)

    def _getindex(self, number: Number, /):
        return (number - self.a1) / self.d

    @property
    def start(self, /) -> Number:
        return self._getitem(self.r.start)

    @property
    def step(self, /) -> Number:
        return self.d * self.r.step

    @property
    def stop(self, /) -> Number:
        return self._getitem(self.r.stop)

    @property
    def last(self, /) -> Number:
        return self._getitem(self.r[-1])

    def iterfunc(reverse, /):
        def __iter__(self, /):
            step = (r := self.r).step
            if reverse:
                start = self.last
                step = -step

            else:
                start = self.start

            return it.islice(it.count(start, self.step * step), len(r))

        return __iter__

    def count(self, number: Number, /) -> int:
        return self.r.count(self._getindex(number))

    def index(self, number: Number, /) -> int:
        return self.r.index(self._getindex(number))

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
    def sized(cls, /, start: Number = 0, step: Number = 1, *, n):
        """Returns a Progression form start with step of size n"""
        if n < 0:
            raise ValueError("size must be non-negative")
        return cls(range(n), start, step)


@dataclass(slots=True, frozen=True)
class GeometricProgression(Sequence):
    a1: int
    r: int
    n: int

    def __getitem__(self, index: int, /):
        if index < 0:
            index += self.n
        if 0 <= index < self.n:
            return self.a1 * self.r**index
        else:
            raise IndexError("GeometricProgression Index out of range.")

    def __len__(self, /):
        return self.n

    def __iter__(self, /) -> Iterator[int]:
        return it.accumulate(it.repeat(self.r, self.n - 1), op.mul, initial=self.a1)

    def __reversed__(self, /) -> Iterator[int]:
        n = self.n - 1
        last = self.a1 * (self.r**n)
        return it.accumulate(it.repeat(self.r, n), op.floordiv, initial=last)

    def __contains__(self, number: int, /) -> bool:
        return self._to_index(number).is_integer()

    def _to_index(self, number: int, /) -> float | int:
        return math.log(number / self.a1, self.r)

    def index(self, number: int, /) -> int:
        if (index := self._to_index(number)).is_integer():
            return math.trunc(index)
        else:
            raise ValueError("Number not in GeometricProgression")

    def count(self, number: int, /) -> int:
        return +(number in self)

    def sum(self, /) -> int:
        return (self.a1 * (1 - self.r**self.n)) // (1 - self.r)


if __name__ == "__main__":
    import builtins

    geoprog = GeometricProgression(2, 2, 10)
    test_list = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
    assert test_list == list(geoprog)
    assert test_list[::-1] == list(reversed(geoprog))
    assert test_list[-3] == geoprog[-3]
    assert test_list[5] == geoprog[5]
    assert test_list.index(128) == geoprog.index(128)
    assert builtins.sum(geoprog) == geoprog.sum()
