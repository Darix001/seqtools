"""This library is directly inspired by itertools, as the idea of conceiving a library
for dealing with seqtools in a more efficient and intuitive way."""

# replace dataclasss for atributes
__all__ = [
    "nwise",
    "permutations",
    "product",
    "sslice",
    "view",
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
    "batched",
]

from .basic import ReverseView as rview
from .basic import SequenceView as view
from .basic import Slice as sslice
from .chain import Chain as chain
from .comb import Batched as batched
from .comb import Nwise as nwise
from .comb import Permutations as permutations
from .comb import Product as product
from .enumerated import Enumerated as enumerated
from .funcs import all_equals, cycle, get
from .progression import ArithmeticProgression as progression
from .progression import GeometricProgression as geometric_progression
from .repeat import Mul as mul
from .repeat import Repeat as repeat
from .repeat import Repeats as repeats
from .zip import Zip as zip
from .zip import ZipLongest as zip_longest
