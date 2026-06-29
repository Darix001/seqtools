from collections import deque
from collections.abc import Iterator
from dataclasses import field
from functools import partial
from itertools import accumulate, chain, islice, pairwise, repeat, tee
from math import factorial, perm, prod, sumprod, trunc
from operator import eq, floordiv, indexOf, methodcaller, mul, sub
from typing import Any, Generic, Unpack

from .bases import TS, TVT, Combinations, Sequence, frozen_dataclass
from .funcs import (
    cycle,
    efficient_nwise,
    get_sizes,
    getitems,
    map_repeat,
    reverse_all,
)
from .repeat import Mul

cumprod = partial(accumulate, func=mul, initial=1)

R_NONE = repeat(None)

NWISE_ITER = {1: zip, 2: pairwise}

EMPTY_ITER = iter(())


def nwise_contains_or_count_deco(func, /):
    def function(self, value, /):
        data = efficient_nwise(self.data, self.r)
        value = repeat(deque(value))
        return func(map(eq, data, value))

    return function


class Nwise(Combinations):
    """Emulates tuples of every r elements of data."""

    def _getitem(self, index, data, r, /) -> Sequence:
        if len(res := data[index : index + r]) != r:
            raise self.index_error()
        return res

    def iterfunc(reverse, /):
        def __iter__(self, /):
            first = data = self.data

            if reverse:
                first = reversed(first)

            if not (r := self.r):
                return repeat((), len(data))

            elif r < 3:
                return NWISE_ITER[r](first)

            else:
                r = range(1, r)
                first = iter(first)

                if not reverse:
                    args = map(islice, repeat(data), r, R_NONE)

                return zip(first, *args)

        return __iter__

    def __len__(self, /):
        return len(self.data) - (self.r - 1) if self else 0

    def __bool__(self, /):
        return self.r <= len(self.data)

    def _index(self, value, start, stop, /):  # Pending implementation
        return super().index(value, start, stop)

    _count = nwise_contains_or_count_deco(sum)

    _contains = nwise_contains_or_count_deco(any)


def product_contains_count_fn(func, fmap, /):
    return lambda self, value, /: func(fmap(self.data * self.r, value))


@frozen_dataclass
class Product(Combinations, Generic[Unpack[TVT]]):
    """Same as it.product but acts as a sequence."""

    data: tuple[Unpack[TVT]]
    r: int = field(kw_only=True, default=1)

    def __bool__(self, /):
        return all(data) if (data := self.data) else True

    def _getitem(self, index, data, r, /):
        # Code grabbed from more_itertools.nth_permutation
        index = range(len(self))[index]
        values = []

        for seq, size in zip(*self._its()):
            index, mod = divmod(index, size)
            values.append(data[mod])

        return reversed(values)

    def __len__(self, /):
        return prod(self.sizes) ** self.r

    @property
    def sizes(self, /) -> Iterator[int]:
        return get_sizes(self.data)

    def iterfunc(reverse, /):

        def __iter__(self, /):
            if not (data := self.data) or not (r := self.r):
                return iter(((),))

            elif not all(data):
                return EMPTY_ITER

            datas = cycle(data)
            nargs = len(data) * r
            *count, n = cumprod(islice(sizes := get_sizes(datas), nargs))
            times = [*map(floordiv, map(floordiv, repeat(n), sizes), count)]
            first, *values = islice(datas, nargs)

            del count[0]

            data = map(repeat, values, count)

            if reverse:
                first = reversed(first)
                data = map(reverse_all, data)

            values[:] = map(chain.from_iterable, data)
            values.insert(0, first)
            values[:-1] = map(
                chain.from_iterable, map(map_repeat, values[:-1], map_repeat(times))
            )

            return zip(*values)

        return __iter__

    def _check(self, value, /) -> bool:
        return type(value) is tuple and (len(value) // self.r) == len(self.data)

    def _its(self, /):
        datas, datas2 = tee(cycle(self.data, self.r))
        return datas, get_sizes(datas2)

    def _index(self, value, start, stop, /) -> int:
        datas, sizes = self._its()
        return trunc(sumprod(map(indexOf, datas, value), cumprod(sizes)))

    def _contains(self, obj: Any):
        return all(map(methodcaller("__contains__", obj), self.data))

    def _count(self, obj: Any):
        return prod(map(methodcaller("count", obj), self.data))

    @classmethod
    def fromargs(cls, /, *args, repeat=1):
        return cls(*args, r=repeat)


class Permutations(Combinations):
    __slots__ = ()
    r: int | None

    def __init__(self, /, data: Sequence, r: int | None = None):
        if r is not None and r < 0:
            raise ValueError("r must be non-negative")
        super().__init__(data, r)

    def __len__(self, /):
        return perm(len(self.data), self.r)

    def _getitem(self, index, data, r, /):
        # Code grabbed from more_itertools.nth_permutation
        if r is None or r == (n := len(data)):
            r, c = n, factorial(n)

        result = [0] * r
        mr = range(len(self))
        index = mr[index]
        q = index * factorial(n) // c if r < n else index

        for d in range(1, n + 1):
            q, i = divmod(q, d)

            if 0 <= n - d < r:
                result[n - d] = i

            if not q:
                break

        return getitems(data, map(sub, result, mr))


del pairwise, mul, accumulate
