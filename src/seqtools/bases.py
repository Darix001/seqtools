from collections import UserDict, UserList
from collections.abc import Callable, Sequence
from dataclasses import dataclass, make_dataclass, replace
from functools import partial, update_wrapper
from typing import Any

from .funcs import get_sizes

OPINT = int | None
NS = Sequence[Sequence]
TS = tuple[Sequence]
frozen_dataclass = partial(dataclass, frozen=True)


def checker(cls, /) -> Callable:
    """Creates a Check method for SubSequence subclasses"""
    return lambda self, obj, /: type(obj) is cls and len(obj) == self.r


def slicer(func: Callable, /) -> Callable:
    """Decorator for functions wich accepts one argument and range arguments"""
    return update_wrapper(lambda obj, /, *args: func(obj, slice(*args)), func)


def datamethod(func: Callable, /) -> Callable:
    return lambda self, /: func(self.data)


def calcsize(func: Callable, /) -> Callable:
    return lambda self, /: func(get_sizes(self.data))


class BaseSequence(Sequence):
    """Base class for all classes in this module."""

    __slots__ = ()
    iterfunc = None
    _replace = replace
    _setattr = object.__setattr__

    def __init_subclass__(cls, /):
        if (factory := cls.iterfunc) is not None:
            cls.__iter__, cls.__reversed__ = map(factory, (None, True))
            del cls.iterfunc

    def value_error(self, value, /):
        raise ValueError(f"{value!r} not in {type(self).__name__}")

    def index_error(self, /):
        raise IndexError(f"{type(self).__name__} object index out of range.")


@frozen_dataclass(order=True)
class SequenceView(BaseSequence):
    """Creates a protected view of a sequence."""

    data: Sequence

    __slots__ = "data"

    index, count = UserList.index, UserList.count

    __class_getitem__ = UserDict.__class_getitem__

    __len__, __contains__ = UserList.__len__, UserList.__contains__

    __getitem__ = UserList.__getitem__

    __iter__ = UserDict.__iter__

    __reversed__, __bool__ = datamethod(reversed), datamethod(bool)

    def __repr__(self, /):
        return f"{type(self).__name__}({self.data!r})"


class ReverseView(SequenceView):
    """Creates a view that emulates the given sequence in reverse order."""

    __slots__ = ()

    __reversed__, __iter__ = SequenceView.__iter__, SequenceView.__reversed__

    def __new__(cls, data: Sequence, /):
        if isinstance(data, cls):
            return SequenceView(data.data)
        else:
            return super().__new__(cls)

    def __getitem__(self, index, /):
        data = self.data
        if isinstance(index, slice):
            i = range(len(data) - 1, -1, -1)[index]
            return type(self)(data[i.start : i.stop : i.step])
        else:
            return data[~index]

    def index(self, value: Any, start: int = 0, stop: OPINT = None, /) -> int:
        n = len(data := self.data)
        getindex = data.index
        if not start and stop is None:
            return ~getindex(value)
        else:
            return ~getindex(value, ~stop + n, ~start + n)


class Size(SequenceView):
    """Base Class for sequence wrappers that transform their sequence size."""

    __slots__ = ()

    def __bool__(self, /):
        return True if self.data and self.r else False


class BaseIndexed(BaseSequence):
    __slots__ = ()

    def __getitem__(self, index, /):
        if type(r := self.r[index]) is int:
            return self._getitem(r)
        else:
            return self._getslice(r)

    def __contains__(self, value, /):
        if indices := self.r:
            return self._contains(value, indices)
        else:
            return False

    def index(self, value, start: int = 0, stop: OPINT = None, /):
        if indices := self.r[start:stop]:
            return self._index(value, indices)
        else:
            self.value_error(value)

    def count(self, value, start: int = 0, stop: OPINT = None, /):
        if indices := self.r[start:stop]:
            return self._count(value, indices)
        else:
            return 0


@frozen_dataclass
class Ranged(BaseIndexed):
    """Base class for classes wich uses an attribute r of type range."""

    __slots__ = "r"
    r: range


RelativeSized = make_dataclass(
    "RelativeSized", (("r", int),), frozen=True, slots=True, bases=(Size,)
)


class SubSequence(SequenceView):
    """Base Class for sequences of sequences"""

    __slots__ = ()

    _index, _count = Sequence.index, Sequence.count

    _contains = Sequence.__contains__

    _check = checker(tuple)

    def __contains__(self, value, /):
        return self._check(value) and self._contains(value)

    def index(self, value, /, start: int = 0, stop: OPINT = None) -> int:
        if self._check(value):
            return self._index(value, start, stop)
        else:
            self.value_error(value)

    def count(self, value, /) -> int:
        return self._count(value) if self._check(value) else 0


class Combinations(RelativeSized, SubSequence):
    """Base Class for combinatoric sequences. A combinations subclass is a type
    of sequence that returns r-length sucessive tuples of different combinations
    of all elements in data."""

    __slots__ = ()

    def __bool__(self, /):
        return not (r := self.r) or len(self.data) >= r

    def __getitem__(self, index, /):
        return tuple(self._getitem(index, self.data, self.r))


del make_dataclass, replace, dataclass, UserList, UserDict
