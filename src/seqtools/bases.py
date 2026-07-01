from __future__ import annotations

from abc import abstractmethod
from collections.abc import Callable, Iterator, Sequence
from functools import partial, update_wrapper, wraps
from typing import Any, Optional, Self, TypeVar, TypeVarTuple

from attrs import evolve, field, frozen

from .funcs import get_sizes

OPINT = Optional[int]
NS = Sequence[Sequence[Any]]
TS = tuple[Sequence[Any]]
TVT = TypeVarTuple("Ts")


def boolen(func, FALSIES={"__bool__": False, "__len__": 0}, /):
    value = FALSIES[func.__name__]

    @wraps(func)
    def function(self, /):
        if (data := self.data) and (r := self.r):
            return func(data, r)
        return value

    return function


def checker(cls, /) -> Callable[..., bool]:
    """Creates a Check method for SubSequence subclasses"""
    return lambda self, obj, /: type(obj) is cls and len(obj) == self.r


def slicer(func: Callable, /) -> Callable:
    """Decorator for functions wich accepts one argument and range arguments"""
    return update_wrapper(lambda obj, /, *args: func(obj, slice(*args)), func)


def datamethod(func: Callable, /) -> Callable:
    return lambda self, /: func(self.data)


def calcsize(func: Callable, /) -> Callable:
    return lambda self, /: func(get_sizes(self.data))


@frozen
class BaseSequence[T](Sequence):
    """Base class for all classes in this module."""

    __slots__ = ()
    iterfunc = None
    _replace = evolve
    _setattr = object.__setattr__

    def __init_subclass__(cls, /) -> None:
        factory: Callable[[bool], Callable[[Self], Iterator[Any]]] | None = cls.iterfunc
        if factory is not None:
            cls.__iter__, cls.__reversed__ = map(factory, (False, True))
            del cls.iterfunc

    def value_error(self, value, /) -> ValueError:
        return ValueError(f"{value!r} not in {type(self).__name__}")

    def index_error(self, /) -> IndexError:
        return IndexError(f"{type(self).__name__} object index out of range.")


base_frozen_dataclass = partial(frozen, init=False, repr=False)

T = TypeVar("T")


@base_frozen_dataclass(slots=True)
class WithData[T](BaseSequence):
    T = T
    data: Sequence[T]


@base_frozen_dataclass
class Size[T](WithData):
    """Base Class for sequence wrappers that transform their sequence size."""

    r: Sequence[int] | int

    def __bool__(self, /):
        return True if self.data and self.r else False


@base_frozen_dataclass
class BaseIndexed[T](Size):
    __slots__ = ()
    r: Sequence[int]

    @abstractmethod
    def _getitem(self, index, /): ...

    @abstractmethod
    def _getslice(self, r, /): ...

    @abstractmethod
    def _count(self, obj, indices, /): ...

    @abstractmethod
    def _index(self, obj, indices, /): ...

    @abstractmethod
    def _contains(self, obj, indices, /): ...

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
            raise self.value_error(value)

    def count(self, value, start: int = 0, stop: OPINT = None, /):
        if indices := self.r[start:stop]:
            return self._count(value, indices)
        else:
            return 0


@base_frozen_dataclass
class Ranged[T](BaseIndexed):
    """Base class for classes wich uses an attribute r of type range."""

    __slots__ = ()
    r: range = field(converter=range)


@base_frozen_dataclass
class RelativeSized[T](Size):
    __slots__ = ()
    r: int


@base_frozen_dataclass
class SubSequence[T](WithData):
    """Base Class for sequences of sequences"""

    __slots__ = ()

    _index, _count = Sequence.index, Sequence.count

    _contains = Sequence.__contains__

    _check = checker(tuple)

    def __contains__(self, value, /):
        return self._check(value) and self._contains(value)

    def index(self, value, /, start: int = 0, stop: int = ...) -> int:
        if self._check(value):
            return self._index(value, start, stop)
        else:
            raise self.value_error(value)

    def count(self, value, /) -> int:
        return self._count(value) if self._check(value) else 0


@base_frozen_dataclass
class Combinations[T](RelativeSized, SubSequence):
    """Base Class for combinatoric sequences. A combinations subclass is a type
    of sequence that returns r-length sucessive tuples of different combinations
    of all elements in data."""

    __slots__ = ()

    @abstractmethod
    def _getitem(self, index, data, r): ...

    def __bool__(self, /):
        return not (r := self.r) or len(self.data) >= r

    def __getitem__(self, index, /):
        return tuple(self._getitem(index, self.data, self.r))
