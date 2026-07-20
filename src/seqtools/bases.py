from __future__ import annotations

import builtins
import itertools
import operator as op
from abc import abstractmethod
from collections.abc import Callable, Iterable, Sequence
from functools import partial, wraps
from sys import maxsize
from typing import (
    Any,
    Generic,
    Optional,
    Self,
    SupportsIndex,
    TypeVar,
    overload,
)

from attrs import field, frozen
from playroom.methodtools import dunder_method_factory

from .funcs import isizes

OPINT = Optional[int]


def boolen(
    func, FALSIES={"__bool__": False, "__len__": 0}, /
) -> Callable[..., bool | int]:
    value = FALSIES[func.__name__]

    @wraps(func)
    def function(self, /):
        if (data := self.data) and (r := self.r):
            return func(data, r)
        return value

    return function


def pos_range(r: int, /) -> range:
    return range(r if r >= 0 else 0)


def checker(cls, /) -> Callable[..., bool]:
    """Creates a Check method for SubSequence subclasses"""
    return lambda self, obj, /: type(obj) is cls and len(obj) == self.r


def check_nargs_on_overload(args: tuple[Any, ...], expected_nargs: int):
    if (nargs := len(args)) != expected_nargs:
        raise TypeError(
            f"Expected {expected_nargs} when passing a {type(args[0])} object, but receive {nargs}"
        )


def datamethod[T](func: Callable[[Sequence], T], /) -> Callable[..., T]:
    return lambda self, /: func(self.data)


def calcsize(func: Callable[[Iterable[int]], int], /) -> Callable[..., int]:
    return lambda self, /: func(isizes(self.data))


T = TypeVar("T")


@frozen
class BaseSequence(Sequence[T], Generic[T]):
    """Base class for all classes in this module."""

    __slots__ = ()
    _setattr = object.__setattr__

    def value_error(self, value, /) -> ValueError:
        return ValueError(f"{value!r} not in {type(self).__name__}")

    def index_error(self, /) -> IndexError:
        return IndexError(f"{type(self).__name__} object index out of range.")


base_frozen = partial(frozen, init=False, repr=False)


@base_frozen(slots=True)
class WithData[T](BaseSequence[T]):
    data: Sequence[T]

    def __replace__(self, /, data) -> Self:
        new = super().__new__()
        new._setattr("data", data or self.data)
        return new


@base_frozen
class Size[T](WithData[T]):
    """Base Class for sequence wrappers that transform their sequence size."""

    def __replace__(self, data=None, r=None) -> Self:
        new = super().__replace__(data)
        new._setattr("r", r or self.r)
        return new

    def __bool__(self, /):
        return True if self.data and self.r else False


@base_frozen
class BaseIndexed[T](Size[T]):
    __slots__ = ()
    r: Sequence[int]

    @abstractmethod
    def _getitem(self, index: SupportsIndex, /) -> T: ...

    @abstractmethod
    def _getslice(self, r, /) -> Self: ...

    @abstractmethod
    def _count(self, obj, indices, /) -> int: ...

    @abstractmethod
    def _index(self, obj, indices, /) -> int: ...

    @abstractmethod
    def _contains(self, obj, indices, /) -> bool: ...

    @overload
    def __getitem__(self, index: SupportsIndex, /) -> T:
        pass

    @overload
    def __getitem__(self, index: slice, /) -> Self:
        pass

    def __getitem__(self, index: SupportsIndex | slice, /) -> T | Self:
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


@base_frozen
class Ranged[T](BaseIndexed[T]):
    """Base class for classes wich uses an attribute r of type range."""

    __slots__ = ()
    r: range

    @dunder_method_factory
    def __len__(func: Callable, /):
        return lambda self, /: func(self.r)

    __bool__ = __len__


@base_frozen
class RelativeSized[T](Size[T]):
    __slots__ = ()
    r: int = field(converter=op.index)
    _min_r = 0

    @r.validator
    def positive_r(self, attribute: str, value: int, /):
        if value < self._min_r:
            raise ValueError(f"r must be an integer greater than {self._min_r}")


@base_frozen
class SubSequence[T](WithData[T]):
    """Base Class for sequences of sequences"""

    __slots__ = ()

    _index, _count = Sequence.index, Sequence.count

    _contains = Sequence.__contains__

    _check = checker(tuple)

    def __contains__(self, value: tuple[T, ...], /):
        return self._check(value) and self._contains(value)

    def index(
        self, value: tuple[T, ...], /, start: int = 0, stop: int = maxsize
    ) -> int:
        if self._check(value):
            return self._index(value, start, stop)
        else:
            raise self.value_error(value)

    def count(self, value: tuple[T, ...], /) -> int:
        return self._count(value) if self._check(value) else 0


@base_frozen
class Combinations[T](RelativeSized[T], SubSequence[T]):
    """Base Class for combinatoric sequences. A combinations subclass is a type
    of sequence that returns r-length sucessive tuples of different combinations
    of all elements in data."""

    __slots__ = ()

    @abstractmethod
    def _getitem(self, index: int, data: Sequence[T], r: int) -> Iterable[T]: ...

    def __bool__(self, /):
        return not (r := self.r) or len(self.data) >= r

    def __getitem__(self, index: SupportsIndex, /) -> tuple[T, ...]:
        return tuple(self._getitem(op.index(index), self.data, self.r))


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

    @property
    def last(self, /) -> T:
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


@frozen(slots=True)
class BaseMap[T](WithData[T]):
    func: Callable[..., T]
    data: Sequence[Any]

    def __len__(self, /):
        return len(self.data)

    @abstractmethod
    def _getitem(self, func: Callable[..., T], item: Any) -> T:
        pass

    def __replace__(self, /, func=None, data=None) -> Self:
        new = super().__replace__(data)
        new._setattr("func", func or self.func)
        return new

    def __getitem__(self, index: SupportsIndex | slice) -> T | Self:
        item = self.data[index]
        if isinstance(index, slice):
            return self.__replace__(item)
        else:
            return self._getitem(self.func, item)

    def __init_subclass__(cls, /, infer_iter: bool = True):
        super().__init_subclass__()
        if not infer_iter:
            return
        fn_name = cls.__name__.lower()
        try:
            func = getattr(builtins, fn_name, None) or getattr(itertools, fn_name)
        except AttributeError as e:
            raise AttributeError(
                "Class name does not match any iterable class on builtins and operator modules."
            ) from e
        else:
            cls.__iter__ = lambda self, /: func(self.func, self.data)
