from .funcs import getitems, CC_MAP, MAP, get_sizes, cycle, efficient_nwise
from .bases import Combinations, Sequence, TS
from .repeat import Mul

from functools import partial
from collections import deque
from collections.abc import Iterator
from operator import eq, mul, indexOf, sub
from math import prod, sumprod, perm, factorial
from itertools import pairwise, islice, accumulate, tee, repeat


cumprod = partial(accumulate, func=mul, initial=1)

R_NONE = repeat(None)

NWISE_ITER = {1:zip, 2:pairwise}

EMPTY_ITER = iter(())


class Nwise(Combinations):
	'''Emulates tuples of every r elements of data.'''

	def _getitem(self, index, data, r, /) -> Sequence:
		if len(res := data[index:index + r]) != r:
			self.index_error()
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

	def _contains(func, /):
		def function(self, value, /):
			data = efficient_nwise(self.data, self.r)
			value = repeat(deque(value))
			return func(map(eq, data, value))
		return function

	def _index(self, value, start, stop, /):
		return Sequence.sub(self.data, value, start, stop)

	_count = _contains(sum)

	@_contains
	def _contains(stream, /):
		return next(filter(None, stream), None)


class Product(Combinations):
	'''Same as it.product but acts as a sequence.'''
	__slots__ = ()
	data:TS

	def __init__(self, /, *args, repeat:int=1):
		super().__init__(args, repeat)

	def __repr__(self, /):
		if not (data := self.data):
			args_repr = ''
		else:
			suffix = ' ' if len(data) == 1 else ', '
			args_repr = f"{data!r}"[:-1] + suffix

		return f"{type(self).__name__}({args_repr}repeat={self.r!r})"

	def __mul__(self, r, /):
		return type(self)(*self.data, repeat=self.r * r)

	def __bool__(self, /):
		return all(data) if (data := self.data) else True

	def _getitem(self, index, data, r, /):
		#Code grabbed from more_itertools.nth_permutation
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
		floordivmap = MAP[-1]

		def __iter__(self, /):
			if not (data := self.data) or not (r := self.r):
				return iter(((),))

			elif not all(data):
				return EMPTY_ITER

			
			datas = cycle(data)
			nargs = len(data) * r
			*count, n = cumprod(islice(sizes := get_sizes(datas), nargs))
			times = [*floordivmap(floordivmap(repeat(n), sizes), count)]
			first, *values = islice(datas, nargs)
			
			del count[0]

			maprepeat, unchain, mapreversed = MAP[:3]
			data = maprepeat(values, count)

			if reverse:
				first = reversed(first)
				data = map(mapreversed, data)

			values[:] = unchain(data)
			values.insert(0, first)
			values[:-1] = unchain(map(maprepeat, values[:-1],
				maprepeat(times)))

			return zip(*values)

		return __iter__


	def _contains(func, fmap, /):
		return lambda self, value, /: func(fmap(self.data * self.r, value))

	def _check(self, value, /) -> bool:
		return type(value) is tuple and (
			len(value) // self.r) == len(self.data)

	def _its(self, /):
		datas, datas2 = tee(cycle(self.data, self.r))
		return datas, get_sizes(datas2)

	def _index(self, value, start, stop, /):
		datas, sizes = self._its()
		return sumprod(map(indexOf, datas, value), cumprod(sizes))

	_contains, _count = map(_contains, (all, prod), CC_MAP)

	@classmethod
	def fromargs(cls, /, *args, repeat=1):
		return cls(Mul(args, repeat))


class Permutations(Combinations):
	__slots__ = ()
	r:int|None

	def __init__(self, /, data:Sequence, r:int|None=None):
		if r is not None and r < 0:
			raise ValueError("r must be non-negative")
		super().__init__(data, r)
	
	def __len__(self, /):
		return perm(len(self.data), self.r)


	def _getitem(self, index, data, r, /):
		#Code grabbed from more_itertools.nth_permutation
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