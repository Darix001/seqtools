from typing import Any
from itertools import repeat
from .funcs import MAP, from_iterable
from .bases import Ranged, RelativeSized, frozen_dataclass, Sequence, OPINT

div_index = {0, -1}.__contains__


@frozen_dataclass
class Repeat(Ranged):
	'''Same as it.repeat but as a sequence.'''
	value:Any

	def __init__(self, /, object:Any, times:int):
		super().__init__(range(times >= 0 and times))
		self._setattr('value', object)

	def __repr__(self, /):
		return f"{type(self).__name__}({self.value!r}, {self.r.stop!r})"
		
	def __len__(self, /):
		return self.r.stop
	
	def __iter__(self, /):
		return repeat(self.value, self.r.stop)

	__reversed__ = __iter__
	def __contains__(self, obj, /):
		return True if self.r.stop and self.value == obj else False

	def __add__(self, value, /):
		if (cls := type(self)) is type(value):
			if (value := self.value) == value.value:
				return cls(value, self.r.stop + value.r.stop)
		return NotImplemented
	
	def _getitem(self, index:int, /):
		return self.value

	def _getslice(self, r, /):
		return type(self)(self.value, len(r))

	def count(self, value, /) -> int:
		return self.r.stop if value in self else 0

	def index(self, value, /) -> int:
		if value in self:
			return 0
		else:
			self.value_error(value)

	def tolist(self, /) -> list:
		return [self.value] * self.r.stop





class Mul(RelativeSized):
	'''Emulates a data sequence multiplied r times.'''
	__slots__ = ()

	def __init__(self, data:Sequence, r:int, /):
		if type(self) is type(data):
			r *= data.r
			data = data.data
		return super().__init__(data, r)

	def __repr__(self, /):
		return f"{type(self).__name__}({self.data!r}, {self.r!r})"

	def __mul__(self, r, /):
		return self.__replace(r=self.r * r)

	def __add__(self, value, /):
		if type(self) is type(value):
			if (data := self.data) == data.data:
				return self._replace(r=self.r + data.r)
		return NotImplemented

	def __getitem__(self, index, /):
		try:
			floordiv, index = divmod(index, len(data := self.data))
			if div_index(floordiv // self.r):
				return data[index]
		except ZeroDivisionError:
			pass
		self.IndexError()

	def __len__(self, /):
		return len(self.data) * self.r

	def __contains__(self, value, /):
		return True if self.r and (value in self.data) else False

	def iterfunc(reverse, /):
		r = MAP[2] if reverse else None
		def __iter__(self, /):
			it = repeat(self.data, self.r)
			if r:
				it = r(it)
			return from_iterable(it)
		return __iter__

	def count(self, value, /) -> int:
		return (r := self.r) and self.data.count(value) * r

	def index(self, value, start=0, stop:OPINT=None, /) -> int:
		index = self.data.index
		if (r := self.r):
			if stop is None and not start:
				return index(value)
			div, start = divmod(start, r)
			if div_index(div):
				return index(value, start, stop % r)
		self.value_error(value)

	def unpack(self, /) -> Sequence:
		return self.data * self.r


class Repeats(Mul):
	'''Emulates a sequence with each elements repeated r times.'''
	__slots__ = ()

	def __mul__(self, n, /):
		return Mul(self, n)
	
	def __getitem__(self, index, /):
		if (r := self.r):
			return self.data[index // r]
		else:
			self.IndexError()

	def iterfunc(reverse, /):
		def __iter__(self, /):
			data = self.data
			if reverse:
				data = reversed(data)
			return from_iterable(MAP[0](data, repeat(self.r)))
		return __iter__

	def index(self, value, start=0, stop:OPINT=None, /) -> int:
		if not (r := self.r):
			self.value_error(value)
		
		index = self.data.index
		
		if stop is None and not start:
			return index(value) * r
		
		start, mod = divmod(start, r)
		return (index(value, start, stop//r) * r) + mod


Sequence.__mul__ = lambda self, n, /: Mul(self, n)