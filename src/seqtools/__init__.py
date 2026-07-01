"""This library is directly inspired by itertools, as the idea of conceiving a library
for dealing with seqtools in a more efficient way."""

from collections.abc import Sequence
from typing import Any, TypeVarTuple, Unpack

# replace dataclasss for atributes
__all__ = [
    "nwise",
    "permutations",
    "product",
    "sslice",
    "sview",
    "rview",
    "chain",
    "enumerated",
    "progression",
    "geometric_progression",
    "zip",
    "zip_longest",
    "repeat",
    "mul",
    "repeats",
    "all_equals",
    "cycle",
    "get",
]

from .basic import ReverseView as rview
from .basic import SequenceView as sview
from .basic import Slice as sslice
from .chain import Chain as chain
from .comb import Nwise as nwise
from .comb import Permutations as permutations
from .comb import Product
from .enumerated import Enumerated as enumerated
from .funcs import all_equals, cycle, get
from .progression import ArithmeticProgression, GeometricProgression
from .repeat import Mul, Repeat, Repeats
from .zip import Zip, ZipLongest

TVT = TypeVarTuple("TVT")

_product_TVT = Unpack[TypeVarTuple("iterables")]


def product[T](*iterables: Sequence[T], repeat: int = 1) -> Product[T]:
    """Same as it.product but as a sequence."""
    return Product[T](iterables, r=repeat)


_zip_TVT = Unpack[TypeVarTuple("iterables")]


def zip(*iterables: _zip_TVT, strict: bool = False) -> Zip[_zip_TVT]:
    """Same as builtins.zip but as a sequence."""
    return Zip[_zip_TVT](iterables, strict=strict)


def zip_longest[T](*iterables: Sequence[Any], fillvalue: Any = None) -> ZipLongest[T]:
    """Same as it.zip_longest but as a sequence."""
    return ZipLongest[T](iterables, fillvalue=fillvalue)


def repeat[V](object: Any, times: int) -> Repeat[V]:
    """Same as it.repeat but as a sequence."""
    return Repeat[V](object, times)


def mul[T](sequence: Sequence[T], n: int) -> Mul[T]:
    """Emulates the result of sequence * n"""
    return Mul[T](sequence, n)


def repeats[T](sequence: Sequence[T], n: int) -> Repeats[T]:
    """Emulates each element in the sequence repeated n times"""
    return Repeats[T](sequence, n)


def progression[PROG_T](
    a1: PROG_T, distance: PROG_T, size: int
) -> ArithmeticProgression[PROG_T]:
    if size < 0:
        raise ValueError("size must be non-negative")
    return ArithmeticProgression[PROG_T](a1, distance, range(size))


def geometric_progression[PROG_T](
    a1: PROG_T, ratio: PROG_T, size: int
) -> GeometricProgression[PROG_T]:
    if size < 0:
        raise ValueError("size must be non-negative")
    return GeometricProgression[PROG_T](a1, ratio, range(size))


a = product("asdfw", repeat=12)
for asd in a:
    print(asd)
