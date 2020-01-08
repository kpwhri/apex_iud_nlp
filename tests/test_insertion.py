import pytest

from apex.algo.iud_insertion import HISTORICAL, INSERTION, IUD, POST_SUCCESS, PRE_SUCCESS


@pytest.mark.parametrize(('s', 'rx'), [
    ('iud inserted 3 months ago', HISTORICAL),
    ('iud inserted 3 months ago', INSERTION),
    ('iud inserted 3 months ago', IUD),
    ('strings were cut', PRE_SUCCESS),
    ('length of strings', POST_SUCCESS),
])
def test_matches(s, rx):
    assert rx.matches(s)
