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
from .progression import ArithmeticProgression as progression
from .progression import GeometricProgression as geometric_progression
from .repeat import Mul as mul
from .repeat import Repeat as repeat
from .repeat import Repeats as repeats
from .zip import Zip, ZipLongest

TVT = TypeVarTuple("TVT")

_product_TVT = Unpack[TypeVarTuple("iterables")]


product = Product.from_args

_zip_TVT = Unpack[TypeVarTuple("iterables")]


def zip(*iterables: _zip_TVT, strict: bool = False) -> Zip[_zip_TVT]:
    """Same as builtins.zip but as a sequence."""
    return Zip[_zip_TVT](iterables, strict=strict)


def zip_longest[T](*iterables: Sequence[Any], fillvalue: Any = None) -> ZipLongest[T]:
    """Same as it.zip_longest but as a sequence."""
    return ZipLongest[T](iterables, fillvalue=fillvalue)
