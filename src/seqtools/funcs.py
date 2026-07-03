import operator as op
from collections import deque
from collections.abc import Generator, Iterable, Iterator, MutableSequence, Sequence
from functools import partial
from itertools import chain, islice, repeat
from typing import Any, Optional

from_iterable = chain.from_iterable
mapper = partial(partial, map)
isizes = mapper(len)
reverse_all = mapper(reversed)
map_repeat = mapper(repeat)

SENTINEL = object()


def cycle[T](data: Sequence[T], n: Optional[int] = None) -> Iterator[T]:
    """Returns an Iterator that repeats the sequence n times.
    if n is None, the iterator repeats endlessly."""
    return from_iterable(repeat(data) if n is None else repeat(data, n))


def infinite_zip(*sequences: Sequence[Any]) -> Iterator[tuple[Any, ...]]:
    return zip(*map(cycle, sequences))


def swap(data: MutableSequence[Any], indices: Iterable[int]) -> None:
    values = op.itemgetter(*indices)(data)
    for index, value in zip(indices, reversed(values)):
        data[index] = value


def efficient_nwise[T](iterable: Iterable[T], n: int) -> Generator[deque[T]]:
    """Yields efficients nwise views of the given iterable re-using a
    collections.deque object."""
    data = deque(islice(iterable := iter(iterable), n - 1), n)
    for _ in map(data.append, iterable):
        yield data


def getitems[T](data: Sequence[T], items: Iterable[Any], /) -> Iterator[T]:
    """fetchs and Yields each item of the data object."""
    return map(partial(op.getitem, data), items)


def check_step(step: int, /):
    if not step:
        raise TypeError("Step Argument must not be zero.")


# def efficient_slice(data:Sequence, slicer:slice):
# 	if isinstance(data, Slice):
# 		return data._replace(r=data.r[slicer])

# 	elif not slicer.start and slicer.stop is None:
# 		match slicer.step:
# 			case None|1:
# 				return SequenceView(data)

# 			case -1:
# 				return ReverseView(data)

# 	return efficient_slice(data, range(len(data))[slicer])


# islice = slicer(efficient_slice)


def get[T](data: Sequence[T], index: int, default: Any = None, /) -> T | Any:
    """Return the value for key if key is in the sequence, else default."""
    try:
        return data[index]
    except IndexError:
        return default


def all_equals(data: Sequence[Any], /) -> bool:
    """Returns True if all items on sequence are equals"""
    return data.count(data[0]) == len(data)


# def sub(data:Sequence, values:Sequence, start:int=0, stop:OPINT=None, /):
# 	first = values[0]
# 	values = Slice(values, range(diff, len()))
# 	while diff:
# 		index = start = data.index(first, start, stop)
# 		for start, value in enumerate(values, start + diff):
# 			if diff := value != data[start]:
# 				start += diff
# 				break
# 	return index

del Any, Iterable, Iterator, Sequence
