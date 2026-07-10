from __future__ import annotations

import builtins
import operator
from collections import ChainMap
from functools import partial
from operator import attrgetter, methodcaller

from .bases import Any, BaseMap, Callable, Self, frozen

scalar_lookup = ChainMap(vars(builtins), vars(operator))

from playroom.methodtools import SetNameFactory


def create_map_methods(
    method_names: str,
    creator: Callable[[str], Callable],
    namespace: dict[str, Any],
    fmt: str = "__{}__",
):
    for method_name in map(fmt.format, method_names.split()):
        namespace[method_name] = creator(method_name)


def submap_method[T](func: Callable) -> Callable[[T], T]:
    return lambda self, /: type(self)(func, self)


def binary_map_method_creator[T](method_name: str) -> Callable[[T, Any], T]:
    return lambda self, value, /: type(self)(methodcaller(method_name, value), self)


def unary_map_method_creator[T](method_name: str) -> Callable[[T], T]:
    return submap_method(scalar_lookup[method_name])


method_factories: dict[str, SetNameFactory] = {
    "binary": SetNameFactory(binary_map_method_creator),
    "unary": SetNameFactory(unary_map_method_creator),
}


def extract_attr(obj: attrgetter) -> str:
    string = f"{obj!r}"
    return string[string.find("(") + 2 : string.find(")") - 1]


@frozen
class Map[T](BaseMap[T]):
    __slots__ = ()
    _getitem = operator.call

    def __getattr__(self, attr: str, /) -> Map[Any]:
        if isinstance(func := self.func, attrgetter):
            attr = f"{extract_attr(func)}.{attr}"
            data = self.data
        else:
            data = self
        return type(self)(attrgetter(attr), data)

    def __call__(self, *args, **kw) -> Map[Any]:
        if isinstance(func := self.func, attrgetter):
            attr = extract_attr(func)
            data = self.data
        else:
            attr = "__call__"
            data = self
        return type(self)(methodcaller(attr, *args, **kw), data)

    namespace = vars()

    __add__ = __sub__ = __mul__ = __truediv__ = __floordiv__ = __mod__ = __pow__ = (
        __divmod__
    ) = method_factories["binary"]

    __radd__ = __rsub__ = __rmul__ = __rtruediv__ = __rfloordiv__ = __rmod__ = (
        __rpow__
    ) = method_factories["binary"]

    __eq__ = __ne__ = __gt__ = __ge__ = __lt__ = __le__ = method_factories["binary"]

    __and__ = __xor__ = __or__ = method_factories["binary"]

    __invert__ = __neg__ = __abs__ = __pos__ = method_factories["unary"]

    def __round__(self, ndigits=None) -> Map[T]:
        func = round if ndigits is None else partial(round, ndigits=ndigits)
        return type(self)(func, self.data)

    def map[D](self, func: Callable[..., D]) -> Map[D]:
        return Map[D](func, self)

    del namespace


class Starmap[T](BaseMap[T]):
    __slots__ = ()

    def _getitem(self, func: Callable[..., T], item: Any) -> T:
        return func(*item)
