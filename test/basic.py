import itertools as it

import more_itertools as mit

import seqtools as st


def test_batched():
    test_data = range(131)
    sbatched = st.batched[int](test_data, 2)
    tbatched = tuple(it.batched(test_data, 2))
    assert mit.iequals(tbatched, sbatched)
    assert tbatched[-1] == sbatched[-1]
    item = sbatched[4]
    assert tbatched[4] == item
    assert len(sbatched) == len(tbatched)


def test_view
