from itertools import accumulate, pairwise, repeat

from .bases import NS, OPINT, Sequence, WithData, calcsize, datamethod
from .funcs import CC_MAP, MAP, from_iterable, get_sizes


class Chain(WithData):
    """Same as it.chain but as a sequence.
    Emulates a Sequence that is the results of the concatenation of multiple sequences.
    This class can emulate the concatenation of sequences of multiple classes.

    Example:

    x = Chain([1,2,3], 'asasa', range(5, 6))
    print(x[0]) #prints 1
    print(x[-1]) #prints 5
    print(x[5]) #prints a
    print(len(x)) #prints 9
    """

    __slots__ = ()
    data: tuple[Sequence]

    __len__ = calcsize(sum)

    __bool__ = datamethod(any)

    def __init__(self, /, *sequences):
        sequences = [*sequences]
        for i, value in enumerate(sequences):
            if isinstance(value, Chain):
                sequences[i : i + 1] = value.data
        self._setattr("data", tuple(sequences))

    def __getitem__(self, index, /):
        data = self.data
        if type(index) is not slice:
            if index < 0:
                data = filter(None, reversed(data))
                for sequence in data:
                    if (size := len(sequence)) >= -index:
                        return sequence[index]
                    index += size
            else:
                for sequence in filter(None, data):
                    if index < (size := len(sequence)):
                        return sequence[index]
                    index -= size
            self.index_error()

        size = [*get_sizes(data)]
        start, stop, step = index.indices(sum(size))
        key = step != 1
        values = []

        for seq, size in zip(data, size):
            values.append(seq := seq[start:stop:step])
            if key:
                start = step - (((size - 1) - start) % step) - 1

            elif start:
                if seq:
                    start = 0
                else:
                    start -= size

            if (stop := (stop - size)) <= 0:
                break

        return type(self)(*values)

    __iter__ = datamethod(from_iterable)

    def __reversed__(self, /):
        return from_iterable(MAP[2](reversed(self.data)))

    def __add__(self, value, /):
        if type(self) is type(value):
            self = self.__copy__()
            self.data += value.data
            return value
        return NotImplemented

    def cc_func(func, fmap, /):  # Count and Contains Function decorator
        return lambda self, obj, /: func(fmap(self.data, repeat(obj)))

    __contains__, count = map(cc_func, (any, sum), CC_MAP)

    del cc_func

    def index(self, value, start=0, stop: OPINT = None, /) -> int:
        data = self.data
        size = [*accumulate(get_sizes(data), initial=0)]
        if stop is None and not start:
            for data, size in zip(data, size):
                try:
                    value = data.index(value)
                except ValueError:
                    pass
                else:
                    return value + size
        else:
            if start < 0:
                start += size[-1]

            if stop < 0:
                stop += size[-1]

            for data, (size, n) in zip(data, pairwise(size)):
                if (r := (start - size)) < n and (n := (stop - size)) > 0:
                    try:
                        value = data.index(value, r, n)
                    except ValueError:
                        pass
                    else:
                        return value + size

        self.value_error(value)

    @classmethod
    def fromsequence(cls, data: NS, /):
        (self := cls())._setattr("data", data)
        return self


del CC_MAP, calcsize
