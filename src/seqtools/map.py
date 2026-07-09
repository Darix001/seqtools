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
    return lambda self, /: type(self)(func, self.data)


def binary_map_method_creator[T](method_name: str) -> Callable[[T, Any], T]:
    return lambda self, value, /: type(self)(
        methodcaller(method_name, value), self.data
    )


def unary_map_method_creator[T](method_name: str) -> Callable[[T], T]:
    return lambda self, /: type(self)(scalar_lookup[method_name], self.data)


METHOD_NAMES = {
    "binary": "add sub mul truediv floordiv mod pow rshift lshift and or xor",
    "unary": "abs neg pos invert",
}


@frozen
class Map[T](BaseMap[T]):
    __slots__ = ()

    def __getattr__(self, attr: str, /) -> Self:
        return type(self)(attrgetter(attr), self.data)

    def __call__(self, *args, **kw) -> Self:
        return type(self)(methodcaller("__call__", *args, **kw), self)

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
        cls = type(self)
        if ndigits is None:
            return cls(round, self.data)
        else:
            return cls(partial(round, ndigits=ndigits), self.data)

    del namespace


class Starmap[T](BaseMap[T]):
    __slots__ = ()
    data: Sequence[Sequence[Any]]
