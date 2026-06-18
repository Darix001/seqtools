from .bases import frozen_dataclass, Size, BaseIndexed, slicer, Sequence
from .funcs import getitems

from functools import wraps
from collections import Counter
from more_itertools import locate
from itertools import islice, chain
from collections.abc import Iterator


@frozen_dataclass
class Indexed(Size, BaseIndexed):
	'''Emulates a sequence that is the result of collect a group of indexes of
	a determined sequence.'''
	r:Sequence[int]

	def __len__(self, /):
		return len(self.r) if self.data else 0

	def __iter__(self, /):
		return getitems(self.data, self.r)

	def __reversed__(self, /):
		return getitems(self.data, reversed(self.r))
	
	def _getitem(self, index:int, /):
		return self.data[index]

	def _getslice(self, r:Sequence[int], /):
		return type(self)(self.data, r)

	def _index(self, obj, indices, /):
		return indices.index(self.data.index(obj))

	def _count(self, obj, indices, /):
		return sum(map(Counter(indices).get, locate(self.data, obj)))

	def unpack(self, /) -> Iterator:
		return getitems(self.data, self.r)


class Slice(Indexed):
	'''Emulates a slice of the given sequence.
	Example:
	>> x = Slice([1, 2, 3, 4, 5, 6, 7], 2, 5)
	>> print(x[2]) #prints 5

	Notes: Negative steps, can cause undefined behavior.
	'''
	__slots__ = ()

	@slicer
	def __init__(self, data:Sequence, slicer:slice, /):
		if isinstance(data, Slice):
			r = data.r[slicer]
		else:
			r = range(*slicer.indices(len(data)))

		super().__init__(data, r)


	def __reversed__(self, /):
		size = len(data := self.data)
		if start := (r := self.r).start:
			return getitems(data, r)
		return islice(chain((None,), reversed(data)),
			size - start, size - self.stop, abs(self.step))
	
	def __iter__(self, /):
		gen = iter(data := self.data)
		r = self.r
		stop, step = r.stop, r.step
		if start := r.start:
			try:
				gen.__setstate__(start)
			except AttributeError:
				return getitems(data, r)
			else:
				stop -= start
				start = 0
		return islice(gen, start, stop, step)

	def _contains(self, value, indices, /):
		try:
			return self.data.index(value,
				indices.start, indices.stop) in indices
		except ValueError:
			pass
		except TypeError:
			return value in iter(self)

	#bool and integer functions decorator
	def boolen(func, FALSIES={'__bool__':False, '__len__':0}, /):
		value = FALSIES[func.__name__]
		@wraps(func)
		def function(self, /):
			if (data := self.data) and (r := self.r):
				return func(data, r)
			return value
		return function

	@boolen
	def __bool__(data, r, /):
		return start < min(len(data), r.stop) if (start := r.start) else True

	@boolen
	def __len__(data, r, /):
		value = min(len(data), r.stop) - r.start
		return - (-value // r.step) if value > 0 else 0

	del boolen

	def __eq__(self, value, /):
		return (type(self) is type(value) and
			self.data is value.data and self.r == value.r)

	def _index(self, value, r, /) -> int:
		if r:
			data = self.data
			index = data.index
			start = r.start
			stop = r.stop
			return r.index(index(value) if not (start or stop)
				else index(value, start, stop))
		self.value_error(value)

	#peging
	def count(self, value, indices, /) -> int:
		if indices:
			try:
				return self.data.count(value, indices.start, indices.stop)
			except TypeError:
				return super().count(value)
		return 0

	def unpack(self, /) -> Iterator:
		return self.data[(r := self.r).start:r.stop:r.step]