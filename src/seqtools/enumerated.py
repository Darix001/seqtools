from collections.abc import Iterator
from itertools import count

from attrs import frozen

from .bases import SubSequence
from .funcs import get

SENTINEL = object()


@frozen
class Enumerated[T](SubSequence[T]):
    """Same as builtins.enumerate but as a sequence."""

    start: int = 0

    def __getitem__(self, index, /) -> tuple[int, T]:
        data = self.data
        value = data[index]
        if index < 0:
            index += len(data)
        return (index + self.start, value)

    def __iter__(self, /) -> Iterator[tuple[int, T]]:
        return enumerate(self.data, self.start)

    def __reversed__(self, /) -> Iterator[tuple[int, T]]:
        data = self.data
        return zip(count(self.start + len(data) - 1, -1), reversed(data))

    def _check(self, value, /) -> bool:
        return type(value) is tuple and len(value) == 2

    def _index(self, value, start, stop, /) -> int:
        data = self.data
        index, obj = value
        if start or (r := self.start):
            i = data.index(obj, start, stop)
            if (r + i) == index:
                return value
        else:
            try:
                if data[index] == value:
                    return index
            except IndexError:
                pass
        raise self.value_error(value)

    def _count(self, value, /) -> int:
        return +self._contains(value)

    def _contains(self, value, /) -> bool:
        index, obj = value
        if r := self.start:
            index = abs(index - r)
        value = get(self.data, index, SENTINEL)
        return value is not SENTINEL and value == obj
