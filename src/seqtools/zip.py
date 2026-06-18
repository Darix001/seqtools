from .bases import (
	SubSequence,
	calcsize,
	TS,
	Sequence,
	NS,
	datamethod,
	get_sizes)

from .funcs import get
from typing import Any
from functools import reduce
from collections.abc import Iterator
from operator import sub, indexOf, itemgetter, getitem
from itertools import zip_longest, chain, islice, repeat


class Zip(SubSequence):
	"""Same as builtins.zip but as a sequence."""
	__slots__ = '_kwval'
	data:TS

	def __init__(self, /, *sequences:TS, strict:bool=False):
		super().__init__(sequences)
		self._setattr('_kwval', strict)

	def __bool__(self, /):
		return True if (data := self.data) and all(data) else False

	__len__ = calcsize(min)

	def __getitem__(self, index, /):
		data = self.data
		if (index_type := type(index)) is tuple:
			return reduce(getitem, index, data)

		data = tuple(map(itemgetter(index), data))

		if index_type is slice:
			return type(self)(*data, strict=self._kwval)

		return data

	def __iter__(self, /):
		return zip(*self.data, strict=self._kwval)

	def __reversed__(self, /):
		return zip(*self._reversegen(self._levels(), self._kwval))

	@staticmethod
	def _reversegen(levels, r, /):
		for i, (data, level) in enumerate(levels):
			data = reversed(data)
			if level:
				if r:
					raise TypeError(f"Sequence #{i} has different size.")
				data = islice(data, level, None)
			yield data

	def _contains(self, value, /):
		try:
			self.index(value)
		except ValueError:
			return
		else:
			return True

	def _count(self, value, /):
		start = 0,
		try:
			for start in enumerate(self.iter_index(value)):
				pass
		except ValueError:
			return start[0]
	def _check(self, value, /):
		return type(value) is tuple and len(value) == len(self.data)

	def _levels(self, /) -> tuple[Sequence, Iterator[tuple[int, int]]]:
		data = self.data
		n = repeat(len(self))
		return zip(data, map(abs, map(sub, n, get_sizes(data))))

	def _index(self, values, start, stop, /):
		if data := self.data:
			if start is not None:
				indices = [seq.index(value, start,
					stop) for value, seq in zip(values, data)]
			
			else:
				indices = [*map(indexOf, data, values)]
			
			maxvalue = max(indices)
			stop = maxvalue + 1
			n = len(data)
			
			while indices.count(maxvalue) != n:
				iterable = enumerate(zip(data, values, indices))
			
				for index, (seq, value, start) in iterable:
					if start != maxvalue:
						indices[index] = seq.index(value, start + 1, stop)
			
			return maxvalue
		
		self.value_error(values)

	
	@classmethod
	def unzip(cls, data:NS, strict:bool=False):
		(new := cls(strict=strict))._setattr('data', data)
		return new


class Zip_longest(Zip):
	'''Same as it.zip_longest but as a sequence.'''
	__slots__ = ()

	def __init__(self, /, *sequences:TS, fillvalue:Any=None):
		super().__init__(sequences, strict=fillvalue)

	datamethod(any)

	__len__ = calcsize(max)

	def __getitem__(self, index, /):
		if isinstance(index, slice):
			return super().__getitem__(index)
		default = self._kwval
		return tuple(get(data, index, default) if level else data[index]
			for data, level in self._levels())

	def __iter__(self, /):
		return zip_longest(*self.data, fillvalue=self._kwval)

	@staticmethod
	def _reversegen(levels, default, /):
		for data, level in levels:
			data = reversed(data)
			if level:
				data = chain(repeat(default, level), data)
			yield data

	@classmethod
	def unzip(cls, data:NS, fillvalue:Any=None):
		(new := cls(fillvalue=fillvalue))._setattr('data', data)
		return new


del Iterator