import itertools as it
from collections.abc import Iterator
from functools import partial
from operator import methodcaller
from random import randint
from types import ModuleType
from typing import Any, Callable, Sequence

import more_itertools as mit

import seqtools as st

rand_number = partial(randint, 10, 100)


def st_agains_it(class_name: str, *args: Any, **kw: Any):
    creator = methodcaller(class_name, *args, **kw)
    st_obj = creator(st)
    compare_st_and_it(st_obj, creator, it)


def compare_st_and_it(
    sequence: Sequence[Any],
    /,
    caller: Callable[[Any], Iterator[Any]],
    module: ModuleType,
):
    index = randint(0, len(sequence) - 1)
    assert mit.iequals(caller(module), sequence)
    assert mit.iequals(reversed(tuple(caller(module))), reversed(sequence))
    assert sequence[index] == (item := mit.nth(caller(module), index)), (
        f"failed test with index: {index}"
    )
    rindex = ~index
    assert sequence[rindex] == item, f"failed test with reverse index: {rindex}"
    assert mit.ilen(caller(module)) == len(sequence)


def test_it():
    st_agains_it(
        "product", range(rand_number()), range(rand_number()), repeat=randint(1, 10)
    )
    st_agains_it("batched", range(x := rand_number()), randint(1, x))
    st_agains_it("repeat", None, rand_number())
