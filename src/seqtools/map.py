import builtins
import operator
from collections import ChainMap
from functools import partial
from operator import attrgetter, methodcaller

from .bases import Any, BaseMap, Callable, Self, Sequence, frozen

scalar_lookup = ChainMap(vars(builtins), vars(operator))


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
    return lambda self, /: type(self)(scalar_lookup[method_name], self)


METHOD_NAMES = {
    "binary": "add sub mul truediv floordiv mod pow rshift lshift and or xor",
    "unary": "abs neg pos invert",
}


def extract_attr(obj: attrgetter) -> str:
    string = f"{obj!r}"
    return string[string.find("(") + 2 : string.find(")") - 1]


@frozen
class Map[T](BaseMap[T]):
    __slots__ = ()
    _getitem = operator.call

    def __getattr__(self, attr: str, /) -> Self:
        if isinstance(func := self.func, attrgetter):
            attr = f"{extract_attr(func)}.{attr}"
            data = self.data
        else:
            data = self
        return type(self)(attrgetter(attr), data)

    def __call__(self, *args, **kw) -> Self:
        if isinstance(func := self.func, attrgetter):
            attr = extract_attr(func)
            data = self.data
        else:
            attr = "__call__"
            data = self
        return type(self)(methodcaller(attr, *args, **kw), data)

    namespace = vars()
    create_map_methods(
        METHOD_NAMES["binary"],
        binary_map_method_creator,
        namespace,
    )
    create_map_methods(
        METHOD_NAMES["binary"], binary_map_method_creator, namespace, "__r{}__"
    )

    create_map_methods(METHOD_NAMES["unary"], unary_map_method_creator, namespace)

    def __divmod__(self, value: Any) -> Self:
        return type(self)(divmod, self)

    def __round__(self, ndigits=None) -> Self:
        func = round if ndigits is None else partial(round, ndigits=ndigits)
        return type(self)(func, self.data)

    del namespace


class Starmap[T](BaseMap[T]):
    __slots__ = ()

    def _getitem(self, func: Callable[..., T], item: Any) -> T:
        return func(*item)
