"""This library is directly inspired by itertools, as the idea of conceiving a library
for dealing with seqtools in a more efficient way."""

from collections.abc import Sequence
from typing import Any, TypeVar, TypeVarTuple, Unpack

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
]

from .basic import ReverseView as rview
from .basic import SequenceView as sview
from .basic import Slice as sslice
from .chain import Chain as chain
from .comb import Nwise as nwise
from .comb import Permutations as permutations
from .comb import Product
from .enumerated import Enumerated as enumerated
from .progression import ArithmeticProgression as progression
from .progression import GeometricProgression as geometric_progression
from .repeat import Mul, Repeat, Repeats
from .zip import Zip, ZipLongest

TVT = TypeVarTuple("TVT")

_product_TVT = Unpack[TypeVarTuple("iterables")]


def product[_product_TVT](
    *iterables: _product_TVT, repeat: int = 1
) -> Product[_product_TVT]:
    """Same as it.product but as a sequence."""
    return Product[_product_TVT](iterables, repeat)


_zip_TVT = Unpack[TypeVarTuple("iterables")]


def zip(*iterables: _zip_TVT, strict: bool = False) -> Zip[_zip_TVT]:
    """Same as builtins.zip but as a sequence."""
    return Zip[_zip_TVT](iterables, strict=strict)


_zip_longest_TVT = Unpack[TypeVarTuple("iterables")]


def zip_longest[_zip_longest_TVT](
    *iterables: _zip_longest_TVT, fillvalue: Any = None
) -> ZipLongest[_zip_longest_TVT]:
    """Same as it.zip_longest but as a sequence."""
    return ZipLongest[_zip_longest_TVT](iterables, fillvalue=fillvalue)


_V = TypeVar("_V")


def repeat[_V](object: Any, times: int) -> Repeat[_V]:
    """Same as it.repeat but as a sequence."""
    return Repeat[_V](object, times)


T = TypeVar("T")


def mul[T](sequence: Sequence[T], n: int) -> Mul[T]:
    """Emulates the result of sequence * n"""
    return Mul[T](sequence, n)


T = TypeVar("T")


def repeats[T](sequence: Sequence[T], n: int) -> Repeats[T]:
    """Emulates each element in the sequence repeated n times"""
    return Repeats[T](sequence, n)
