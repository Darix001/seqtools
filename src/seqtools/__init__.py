"""This library is directly inspired by itertools, as the idea of conceiving a library
for dealing with seqtools in a more efficient way."""

from collections.abc import Sequence
from typing import Any

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


def product(*iterables: tuple[Sequence], repeat: int = 1) -> Product:
    return Product(iterables, repeat)


def zip(*iterables: tuple[Sequence], strict: bool = False) -> Zip:
    return Zip(iterables, strict=strict)


def zip_longest(*iterables: tuple[Sequence], fillvalue: Any = None) -> ZipLongest:
    return ZipLongest(iterables, fillvalue=fillvalue)


def repeat(object: Any, times: int) -> Repeat:
    return Repeat(object, times)


def mul(sequence: Sequence, times: int) -> Mul:
    return Mul(sequence, times)


def repeats(sequence: Sequence, times: int) -> Repeats:
    return Repeats(sequence, times)
