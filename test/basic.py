import itertools as it

import more_itertools as mit

import seqtools as st


def test_batched():
    test_data = range(131)
    sbatched = st.batched(test_data, 2)
    assert mit.iequals(sbatched, it.batched(test_data, 2))
